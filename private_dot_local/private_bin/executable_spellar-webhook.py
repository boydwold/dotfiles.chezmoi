#!/usr/bin/env python3
"""
Spellar → Obsidian Webhook Server
Receives meeting recordings from Spellar and saves them to your Obsidian vault.
"""

import cgi
import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from pathlib import Path

# Configuration
OBSIDIAN_VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", "/path/to/your/vault")
NOTES_FOLDER = os.environ.get("NOTES_FOLDER", "Meeting Notes")
TRANSCRIPTS_FOLDER = os.environ.get("TRANSCRIPTS_FOLDER", "Meeting Transcripts")
ATTACHMENTS_FOLDER = os.environ.get("ATTACHMENTS_FOLDER", "attachments/spellar")
DAILY_NOTES_FOLDER = os.environ.get("DAILY_NOTES_FOLDER", "Daily Notes")
PORT = int(os.environ.get("PORT", 8765))
LOG_REQUESTS = os.environ.get("LOG_REQUESTS", "true").lower() == "true"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]}")

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "service": "spellar-obsidian-webhook",
            "vault": OBSIDIAN_VAULT_PATH,
            "notes_folder": NOTES_FOLDER
        }).encode())

    def read_chunked(self):
        chunks = []
        while True:
            line = self.rfile.readline().decode('utf-8').strip()
            if not line:
                break
            chunk_size = int(line.split(';')[0], 16)
            if chunk_size == 0:
                self.rfile.readline()
                break
            chunk = self.rfile.read(chunk_size)
            chunks.append(chunk)
            self.rfile.readline()
        return b''.join(chunks)

    def do_POST(self):
        transfer_encoding = self.headers.get("Transfer-Encoding", "")
        content_length = int(self.headers.get("Content-Length", 0))

        if transfer_encoding.lower() == "chunked":
            body = self.read_chunked()
        else:
            body = self.rfile.read(content_length)

        if LOG_REQUESTS:
            print(f"\n{'='*60}")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Incoming webhook")
            print(f"Path: {self.path}")
            print(f"Headers: {dict(self.headers)}")
            try:
                formatted = json.dumps(json.loads(body), indent=2)
                print(f"Body:\n{formatted[:5000]}{'...(truncated)' if len(formatted) > 5000 else ''}")
            except:
                print(f"Body (raw): {body[:2000]}")
            print(f"{'='*60}\n")

        if WEBHOOK_SECRET:
            incoming_secret = self.headers.get("Spwebhooksecret", "")
            if incoming_secret != WEBHOOK_SECRET:
                print(f"Warning: Invalid webhook secret")
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Invalid secret"}).encode())
                return

        try:
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" in content_type:
                data = self.parse_multipart(body, content_type)
            else:
                data = json.loads(body) if body else {}

            # Send response IMMEDIATELY before processing (audio download can take minutes)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode())

            # Process in background thread to avoid blocking
            import threading
            thread = threading.Thread(target=self.process_meeting_safe, args=(data,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            print(f"Error processing webhook: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
            except:
                pass  # Connection may already be closed

    def process_meeting_safe(self, data):
        """Wrapper to catch exceptions in background thread."""
        try:
            self.process_meeting(data)
        except Exception as e:
            print(f"Error processing meeting: {e}")
            import traceback
            traceback.print_exc()

    def parse_multipart(self, body, content_type):
        environ = {
            'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': content_type,
            'CONTENT_LENGTH': len(body),
        }
        fs = cgi.FieldStorage(fp=BytesIO(body), environ=environ, keep_blank_values=True)

        data = {}
        for key in fs.keys():
            field = fs[key]
            if isinstance(field, list):
                data[key] = [f.value for f in field]
            elif field.filename:
                print(f"Found file: {key} = {field.filename} ({field.type})")
                if 'audio' in key.lower() or 'recording' in key.lower() or field.type.startswith('audio/'):
                    data['_audio_data'] = field.file.read()
                    data['_audio_filename'] = field.filename
            else:
                value = field.value
                if isinstance(value, str) and value.startswith('{'):
                    try:
                        value = json.loads(value)
                    except:
                        pass
                data[key] = value
                print(f"Found field: {key} = {str(value)[:200]}{'...' if len(str(value)) > 200 else ''}")
        return data

    def process_meeting(self, data):
        """Process Spellar webhook and create: summary note, transcript note, daily note entry."""

        # Extract meeting data
        if "Spellar-meeting-key" in data:
            meeting_data = data["Spellar-meeting-key"]
            if isinstance(meeting_data, str):
                meeting_data = json.loads(meeting_data)
        else:
            meeting_data = data

        title = meeting_data.get("title", "Untitled Meeting")
        raw_transcript = meeting_data.get("transcript", [])
        summary = meeting_data.get("summary", {})
        audio_url = meeting_data.get("audio_link", "") or meeting_data.get("audioUrl", "")
        timestamp = meeting_data.get("time", "") or meeting_data.get("timestamp", datetime.now().isoformat())
        tags = meeting_data.get("tags", [])
        duration_seconds = meeting_data.get("duration", 0)

        # Parse timestamp and convert to local timezone
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            dt = dt.astimezone()  # Convert UTC to local timezone
        except:
            dt = datetime.now()

        # Format duration
        if duration_seconds:
            hours, remainder = divmod(int(duration_seconds), 3600)
            minutes = remainder // 60
            duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        else:
            duration_str = ""

        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        time_display = dt.strftime("%I:%M %p").lstrip("0")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        filename = f"{date_str} {safe_title}"

        # Ensure directories exist
        vault = Path(OBSIDIAN_VAULT_PATH)
        notes_path = vault / NOTES_FOLDER
        transcripts_path = vault / TRANSCRIPTS_FOLDER
        attachments_path = vault / ATTACHMENTS_FOLDER
        daily_path = vault / DAILY_NOTES_FOLDER

        for p in [notes_path, transcripts_path, attachments_path, daily_path]:
            p.mkdir(parents=True, exist_ok=True)

        # === PREPARE AUDIO PATHS (download happens last) ===
        audio_link = ""
        audio_embed = ""
        audio_file_path = None
        if audio_url:
            url_lower = audio_url.lower().split('?')[0]
            ext = "mp4" if ".mp4" in url_lower else "m4a" if ".m4a" in url_lower else "mp3" if ".mp3" in url_lower else "mp4"
            audio_filename = f"{filename}.{ext}"
            audio_file_path = attachments_path / audio_filename
            audio_link = f"[[{ATTACHMENTS_FOLDER}/{audio_filename}]]"
            audio_embed = f"![[{ATTACHMENTS_FOLDER}/{audio_filename}]]"

        # === FORMAT TRANSCRIPT ===
        if isinstance(raw_transcript, list):
            transcript_lines = []
            for segment in raw_transcript:
                speaker = segment.get("speaker", "Unknown")
                text = segment.get("transcript", "")
                if text:
                    transcript_lines.append(f"**{speaker}:** {text.strip()}")
            transcript_text = "\n\n".join(transcript_lines)
        else:
            transcript_text = str(raw_transcript) if raw_transcript else ""

        # === EXTRACT SUMMARY ===
        if isinstance(summary, dict):
            print(f"Summary keys: {list(summary.keys())}")
            brief = summary.get("summary", "") or summary.get("brief", "")
            decisions = summary.get("decisions", [])
            topics = summary.get("topics", [])
            tasks = summary.get("tasks", [])
        else:
            brief = str(summary) if summary else ""
            decisions = []
            topics = []
            tasks = []

        # Format tags
        tags_yaml = "\n".join(f'  - "{tag}"' for tag in tags) if tags else '  - meeting\n  - spellar'
        tags_inline = ", ".join(tags[:3]) if tags else ""

        # === 1. SUMMARY FILE (most important) ===
        summary_note = f"""---
processed: false
title: "{title}"
date: {date_str}
time: "{time_str}"
type: meeting-note
source: spellar
duration: "{duration_str}"
tags:
{tags_yaml}
---

# {title}

**Date:** {dt.strftime("%B %d, %Y at %I:%M %p")}
**Duration:** {duration_str}
**Recording:** {audio_embed}
**Transcript:** [[{TRANSCRIPTS_FOLDER}/{filename}|Full Transcript]]

"""
        if brief:
            summary_note += f"## Summary\n\n{brief}\n\n"

        if decisions:
            summary_note += "## Decisions\n\n"
            for decision in decisions:
                if isinstance(decision, dict):
                    d_text = decision.get("decision", "") or decision.get("text", "") or decision.get("title", "")
                else:
                    d_text = str(decision)
                if d_text:
                    summary_note += f"- {d_text}\n"
            summary_note += "\n"

        if topics:
            summary_note += "## Topics\n\n"
            for topic in topics:
                t_title = topic.get("title", "")
                t_context = topic.get("context", "")
                t_points = topic.get("key_points", [])

                summary_note += f"### {t_title}\n\n"
                if t_context:
                    summary_note += f"{t_context}\n\n"
                if t_points:
                    for point in t_points:
                        summary_note += f"- {point}\n"
                    summary_note += "\n"

        if tasks:
            summary_note += "## Action Items\n\n"
            for task in tasks:
                t_title = task.get("title", "")
                t_context = task.get("context", "")
                if t_title:
                    summary_note += f"- [ ] **{t_title}**"
                    if t_context:
                        summary_note += f": {t_context}"
                    summary_note += "\n"
            summary_note += "\n"

        summary_file = notes_path / f"{filename}.md"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_note)
        print(f"✓ Saved summary: {summary_file}")

        # === 2. TRANSCRIPT FILE ===
        transcript_note = f"""---
title: "{title}"
date: {date_str}
time: "{time_str}"
type: meeting-transcript
source: spellar
duration: "{duration_str}"
tags:
{tags_yaml}
---

# {title} - Transcript

**Date:** {dt.strftime("%B %d, %Y at %I:%M %p")}
**Duration:** {duration_str}
**Summary:** [[{NOTES_FOLDER}/{filename}|View Summary]]

## Recording

{audio_embed}

## Full Transcript

{transcript_text}
"""
        transcript_file = transcripts_path / f"{filename}.md"
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript_note)
        print(f"✓ Saved transcript: {transcript_file}")

        # === 3. DAILY NOTE ENTRY ===
        daily_note_file = daily_path / f"{date_str}.md"

        # Create one-line summary for daily note
        if brief:
            # Take first sentence or first 150 chars
            one_liner = brief.split('.')[0].strip()
            if len(one_liner) > 150:
                one_liner = one_liner[:147] + "..."
        else:
            one_liner = f"Meeting with topics: {tags_inline}" if tags_inline else "Meeting recorded"

        meeting_entry = f"""
### 🎙️ {time_display} — {title} ({duration_str})

{one_liner}

→ [[{NOTES_FOLDER}/{filename}|Summary]] | [[{TRANSCRIPTS_FOLDER}/{filename}|Transcript]]

"""
        # Append to daily note with retry for cloud sync locks
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if daily_note_file.exists():
                    with open(daily_note_file, "a", encoding="utf-8") as f:
                        f.write(meeting_entry)
                else:
                    daily_content = f"""---
date: {date_str}
type: daily-note
---

# {dt.strftime("%A, %B %d, %Y")}

## Meetings
{meeting_entry}"""
                    with open(daily_note_file, "w", encoding="utf-8") as f:
                        f.write(daily_content)
                print(f"✓ Updated daily note: {daily_note_file}")
                break
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"Daily note locked, retrying in 1s... ({attempt + 1}/{max_retries})")
                    time.sleep(1)
                else:
                    print(f"Warning: Could not update daily note (file locked by sync): {e}")

        # === 4. AUDIO DOWNLOAD (last, slowest) ===
        if audio_url and audio_file_path:
            try:
                import urllib.request
                if audio_file_path.exists():
                    print(f"Audio already exists: {audio_file_path}")
                else:
                    print(f"Downloading audio...")
                    urllib.request.urlretrieve(audio_url, audio_file_path)
                    print(f"✓ Saved audio: {audio_file_path}")
            except Exception as e:
                print(f"Warning: Failed to download audio: {e}")


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


def main():
    log_status = "ON" if LOG_REQUESTS else "OFF"
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  Spellar → Obsidian Webhook Server                       ║
╠══════════════════════════════════════════════════════════╣
║  Vault:       {OBSIDIAN_VAULT_PATH:<41} ║
║  Summaries:   {NOTES_FOLDER:<41} ║
║  Transcripts: {TRANSCRIPTS_FOLDER:<41} ║
║  Audio:       {ATTACHMENTS_FOLDER:<41} ║
║  Daily Notes: {DAILY_NOTES_FOLDER:<41} ║
║  Port:        {PORT:<41} ║
║  Logging:     {log_status:<41} ║
╚══════════════════════════════════════════════════════════╝

Webhook URL: http://localhost:{PORT}/webhook

Waiting for Spellar webhooks...
""")

    server = ReusableHTTPServer(("0.0.0.0", PORT), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
