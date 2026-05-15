# -*- coding: utf-8 -*-
"""Apply all IDEALZ indexd redesign patches to index - Copy.html"""
import re
from pathlib import Path

HTML_PATH = Path(r"c:\Users\Yusrim\Downloads\index - Copy.html")
CSS_PATH = Path(r"c:\Users\Yusrim\Downloads\idealz-indexd-style.css")
SETTINGS_SNIP = Path(r"c:\Users\Yusrim\Downloads\settings_card_snippet.html")


def patch_html(html: str) -> str:
    # Hero dots
    if "hero-dots" not in html:
        html = html.replace(
            '        <div class="hero">\n            <motion class="hero-top">',
            '        <motion class="hero">\n            <div class="hero-dots"></div>\n            <div class="hero-top">',
        )
        html = html.replace(
            '        <div class="hero">\n            <div class="hero-top">',
            '        <div class="hero">\n            <div class="hero-dots"></div>\n            <div class="hero-top">',
        )

    # Settings card
    if "localBackupStatus" not in html and SETTINGS_SNIP.exists():
        snip = SETTINGS_SNIP.read_text(encoding="utf-8")
        html = re.sub(
            r'        <div class="card">\s*\n\s*<div class="card-title" style="margin-bottom:14px;">🔄 Data Sync & Backup</div>.*?'
            r'<button class="btn btn-ghost btn-full" onclick="importFromText\(\)">📥 Import from Pasted Text</button>\s*\n        </div>',
            snip.rstrip(),
            html,
            count=1,
            flags=re.DOTALL,
        )

    # Terminal ticker
    if "termTicker" not in html:
        ticker = """
    <!-- TERMINAL TICKER -->
    <div class="terminal-ticker" id="termTicker">
        <div class="ticker-track" id="tickerTrack">
            <span class="ticker-item"><span class="ticker-dot"></span> SYSTEM ONLINE</span>
            <span class="ticker-item">STUDENTS: <span id="tkStudents">—</span></span>
            <span class="ticker-item">SESSIONS: <span id="tkSessions">—</span></span>
            <span class="ticker-item">LAST SYNC: <span id="tkSync">—</span></span>
            <span class="ticker-item">AVG ATTENDANCE: <span id="tkAtt">—</span></span>
            <span class="ticker-item">DATA INTEGRITY: 100%</span>
            <span class="ticker-item">ENCRYPTION: AES-256</span>
            <span class="ticker-item"><span class="ticker-dot"></span> SYSTEM ONLINE</span>
            <span class="ticker-item">STUDENTS: <span id="tkStudents2">—</span></span>
            <span class="ticker-item">SESSIONS: <span id="tkSessions2">—</span></span>
            <span class="ticker-item">LAST SYNC: <span id="tkSync2">—</span></span>
            <span class="ticker-item">AVG ATTENDANCE: <span id="tkAtt2">—</span></span>
            <span class="ticker-item">DATA INTEGRITY: 100%</span>
            <span class="ticker-item">ENCRYPTION: AES-256</span>
        </div>
    </div>

"""
        html = html.replace("    <!-- BOTTOM NAV -->", ticker + "    <!-- BOTTOM NAV -->")

    # Sync modal
    old_sync = """            <motion class="btn-row" style="margin-bottom:16px;">
                <button class="btn btn-primary btn-full" onclick="exportAllData()">📤 Export All Data (JSON)</button>
            </div>
            <div class="form-group"><label>Import from File</label>
                <button class="btn btn-ghost btn-full" onclick="document.getElementById('syncImportFile').click()">📥
                    Choose JSON File</button>
                <input type="file" id="syncImportFile" accept=".json" style="display:none"
                    onchange="importFromFile(this)">
            </div>""".replace("<motion class=", "<div class=")

    new_sync = """            <div class="btn-row admin-only-block" style="margin-bottom:16px;">
                <button class="btn btn-primary btn-full" onclick="exportAllData()">📤 Export All Data (JSON)</button>
            </div>
            <div class="admin-only-block">
                <div class="form-group"><label>Import from File</label>
                    <button class="btn btn-ghost btn-full" onclick="document.getElementById('syncImportFile').click()">📥 Choose JSON File</button>
                    <input type="file" id="syncImportFile" accept=".json" style="display:none" onchange="importFromFile(this)">
                </div>
            </div>
            <div class="notice edit-only" id="syncNoticeOperator" style="display:none;">🔒 Export & import is admin-only. You can view and sync data but cannot bulk export or import.</motion>""".replace("</motion>", "</div>")

    if "syncNoticeOperator" not in html:
        html = html.replace(
            """            <div class="btn-row" style="margin-bottom:16px;">
                <button class="btn btn-primary btn-full" onclick="exportAllData()">📤 Export All Data (JSON)</button>
            </div>
            <div class="form-group"><label>Import from File</label>
                <button class="btn btn-ghost btn-full" onclick="document.getElementById('syncImportFile').click()">📥
                    Choose JSON File</button>
                <input type="file" id="syncImportFile" accept=".json" style="display:none"
                    onchange="importFromFile(this)">
            </div>""",
            new_sync,
        )

    # Local backup JS
    if "BACKUP_KEY" not in html:
        backup_js = r'''
        const BACKUP_KEY = 'idealz_backup_v2';
        const BACKUP_TS_KEY = 'idealz_backup_ts';
        const AUTO_BACKUP_INTERVAL = 5 * 60 * 1000;

        function triggerLocalBackup() {
            try {
                const snapshot = JSON.stringify(db);
                localStorage.setItem(BACKUP_KEY, snapshot);
                localStorage.setItem(BACKUP_TS_KEY, new Date().toISOString());
                updateBackupStatus();
                showToast('💾 Local backup saved!');
            } catch(e) { showToast('⚠️ Backup failed: ' + e.message); }
        }

        function updateBackupStatus() {
            const ts = localStorage.getItem(BACKUP_TS_KEY);
            const el = document.getElementById('lastBackupTime');
            if (!el) return;
            if (!ts) { el.textContent = 'Never'; return; }
            const d = new Date(ts);
            const mins = Math.round((Date.now() - d.getTime()) / 60000);
            if (mins < 1) el.textContent = 'Just now';
            else if (mins < 60) el.textContent = mins + ' min ago';
            else el.textContent = d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
        }

        function restoreFromBackup() {
            const snap = localStorage.getItem(BACKUP_KEY);
            if (!snap) { showToast('⚠️ No backup found'); return; }
            if (!confirm('Restore from last local backup? Current data will be overwritten.')) return;
            try {
                db = JSON.parse(snap);
                saveDB();
                refreshHome(); renderStudentList(); renderVolunteerList(); renderHistory();
                showToast('✅ Restored from local backup!');
            } catch(e) { showToast('❌ Restore failed'); }
        }

        function updateDataSectionForRole() {
            const role = window.currentRole || 'public';
            const opNote = document.getElementById('operatorDataNote');
            if (opNote) opNote.style.display = (role === 'operator') ? 'block' : 'none';
        }

        function updateTicker() {
            const s = db.students.length;
            const ses = db.sessions.length;
            const ts = new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
            let allRates2 = [];
            for (const st of db.students) {
                const a = getMemberAttendance(st.id, 'student');
                if (a.sessions > 0) allRates2.push(a.rate);
            }
            const avg = allRates2.length ? Math.round(allRates2.reduce((a,b)=>a+b,0)/allRates2.length) : 0;
            ['tkStudents','tkStudents2'].forEach(id => { const el=document.getElementById(id); if(el) el.textContent=s; });
            ['tkSessions','tkSessions2'].forEach(id => { const el=document.getElementById(id); if(el) el.textContent=ses; });
            ['tkSync','tkSync2'].forEach(id => { const el=document.getElementById(id); if(el) el.textContent=ts; });
            ['tkAtt','tkAtt2'].forEach(id => { const el=document.getElementById(id); if(el) el.textContent=avg+'%'; });
            updateBackupStatus();
        }

        setInterval(() => {
            if (window.currentRole === 'admin' || window.currentRole === 'operator') triggerLocalBackup();
        }, AUTO_BACKUP_INTERVAL);

        window.addEventListener('beforeunload', () => {
            if (window.currentRole === 'admin' || window.currentRole === 'operator') triggerLocalBackup();
        });
'''
        html = html.replace(
            "        function saveDB() { localStorage.setItem(DB_KEY, JSON.stringify(db)); }",
            "        function saveDB() { localStorage.setItem(DB_KEY, JSON.stringify(db)); }\n" + backup_js,
        )

    if "updateTicker();" not in html:
        html = html.replace(
            "            renderHomeLeaderboard(sorted.slice(0, 5));\n        }",
            "            renderHomeLeaderboard(sorted.slice(0, 5));\n            updateTicker();\n        }",
        )

    old_role = """        window.updateUIForRole = function () {
            const role = window.currentRole || 'public';
            const user = window.currentUser;

            // Update body class
            document.body.classList.remove('role-admin', 'role-operator', 'role-public', 'role-pending');
            document.body.classList.add('role-' + role);

            // Update auth button
            const label = document.getElementById('authLabel');
            const avatar = document.getElementById('authAvatar');
            if (user) {
                label.textContent = role === 'admin' ? '👑 Admin' : role === 'operator' ? '🛠 Operator' : '⏳ Pending';
                if (user.photoURL) { avatar.src = user.photoURL; avatar.style.display = 'block'; }
            } else {
                label.textContent = 'Sign In';
                avatar.style.display = 'none';
            }

            // Reload data from Firebase
            if (typeof loadFromFirebase === 'function') loadFromFirebase();
        };"""

    new_role = """        window.updateUIForRole = function () {
            const role = window.currentRole || 'public';
            const user = window.currentUser;

            document.body.classList.remove('role-admin','role-operator','role-public','role-pending');
            document.body.classList.add('role-' + role);

            const label = document.getElementById('authLabel');
            const avatar = document.getElementById('authAvatar');
            if (user) {
                label.textContent = role==='admin' ? '👑 ADMIN' : role==='operator' ? '🛠 OPS' : '⏳ PENDING';
                if (user.photoURL) { avatar.src=user.photoURL; avatar.style.display='block'; }
            } else {
                label.textContent = 'SIGN IN';
                avatar.style.display = 'none';
            }

            const syncNote = document.getElementById('syncNoticeOperator');
            if (syncNote) syncNote.style.display = (role==='operator') ? 'block' : 'none';
            if (typeof updateDataSectionForRole === 'function') updateDataSectionForRole();
            if (typeof loadFromFirebase === 'function') loadFromFirebase();
            updateBackupStatus();
        };"""

    html = html.replace(old_role, new_role)

    if "INDEXD VISUAL EFFECTS" not in html:
        effects = open(Path(__file__).parent / "visual_effects.js.txt", encoding="utf-8").read() if (Path(__file__).parent / "visual_effects.js.txt").exists() else ""
        if effects:
            html = html.replace(
                "        window.updateUIForRole();\n    </script>",
                effects + "\n        window.updateUIForRole();\n    </script>",
            )

    return html


def main():
    html = HTML_PATH.read_text(encoding="utf-8")

    if CSS_PATH.exists():
        css = CSS_PATH.read_text(encoding="utf-8").strip()
        html = re.sub(r"<style>.*?</style>", f"<style>\n{css}\n    </style>", html, count=1, flags=re.DOTALL)
        print("Replaced CSS")
    else:
        print("CSS file missing - skipping style block")

    html = patch_html(html)
    HTML_PATH.write_text(html, encoding="utf-8")
    print("Saved", HTML_PATH)


if __name__ == "__main__":
    main()
