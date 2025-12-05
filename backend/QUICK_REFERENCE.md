# Quick Reference Guide - HTML Rendering Feature

## Summary of Changes

All `/research/*` endpoints now return a `report_html` field containing the fully rendered HTML report. This eliminates the need for a separate API call to render the markdown.

## API Response Structure

### Before (Old)
```json
{
  "status": "completed",
  "report_path": "reports/xxx.md",
  "pdf_path": "reports/xxx.pdf",
  "view_url": "http://localhost:8000/reports/view/xxx.md",
  "pdf_url": "http://localhost:8000/static/reports/xxx.pdf"
}
```

### After (New)
```json
{
  "status": "completed",
  "report_path": "reports/xxx.md",
  "report_html": "<!DOCTYPE html>...</html>",  ← NEW!
  "pdf_path": "reports/xxx.pdf",
  "view_url": "http://localhost:8000/reports/view/xxx.md",
  "pdf_url": "http://localhost:8000/static/reports/xxx.pdf"
}
```

## Usage Examples

### 1. Overview Research
```bash
curl -X POST http://localhost:8000/research/overview \
  -H "Content-Type: application/json" \
  -d '{"topic": "Machine Learning", "depth": "short"}'
```

**Response includes:**
- `report_html` - Ready-to-display HTML

### 2. Compare Research
```bash
curl -X POST http://localhost:8000/research/compare \
  -H "Content-Type: application/json" \
  -d '{"item_a": "Python", "item_b": "JavaScript", "depth": "medium"}'
```

**Response includes:**
- `report_html` - Ready-to-display HTML

### 3. Custom Research
```bash
curl -X POST http://localhost:8000/research/custom \
  -H "Content-Type: application/json" \
  -d '{"query": "AI vs Machine Learning", "depth": "deep"}'
```

**Response includes:**
- `report_html` - Ready-to-display HTML

### 4. View Report (Updated)

**JSON format (default):**
```bash
curl http://localhost:8000/reports/view/20251205_131100_overview.md
```

Returns:
```json
{
  "html": "<!DOCTYPE html>...</html>",
  "title": "20251205_131100_overview.md"
}
```

**HTML format (new):**
```bash
curl http://localhost:8000/reports/view/20251205_131100_overview.md?format=html
```

Returns raw HTML with `Content-Type: text/html`

## Frontend Integration

### Simple JavaScript Example
```javascript
// Call any research endpoint
const response = await fetch('http://localhost:8000/research/overview', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ topic: 'AI', depth: 'short' })
});

const result = await response.json();

// Render HTML directly
document.getElementById('report').innerHTML = result.report_html;

// Or use in an iframe for safety
const iframe = document.createElement('iframe');
iframe.srcdoc = result.report_html;
document.body.appendChild(iframe);
```

### React Example
```jsx
function ResearchReport({ topic }) {
  const [html, setHtml] = useState('');
  const [loading, setLoading] = useState(false);

  const runResearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/research/overview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, depth: 'short' })
      });
      const result = await response.json();
      setHtml(result.report_html);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={runResearch}>Generate Report</button>
      {loading && <p>Loading...</p>}
      <iframe srcDoc={html} style={{ width: '100%', height: '800px' }} />
    </div>
  );
}
```

### Vue Example
```vue
<template>
  <div>
    <button @click="runResearch">Generate Report</button>
    <div v-if="loading">Loading...</div>
    <iframe :srcdoc="html" style="width: 100%; height: 800px"></iframe>
  </div>
</template>

<script>
export default {
  data() {
    return {
      html: '',
      loading: false
    };
  },
  methods: {
    async runResearch() {
      this.loading = true;
      try {
        const response = await fetch('http://localhost:8000/research/overview', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic: 'AI', depth: 'short' })
        });
        const result = await response.json();
        this.html = result.report_html;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

## Benefits

✅ **Single API Call** - No need to call `/reports/view` separately
✅ **Immediate Rendering** - HTML is pre-generated during report creation
✅ **Reduced Latency** - Frontend gets everything in one response
✅ **Backward Compatible** - All existing endpoints still work
✅ **Flexible** - Frontend can use HTML, PDF, or markdown

## File Locations

- **Reports Directory**: `reports/`
- **Markdown Reports**: `reports/YYYYMMDD_HHMMSS_mode.md`
- **PDF Reports**: `reports/YYYYMMDD_HHMMSS_mode.pdf`
- **Test Script**: `test_html_generation.py`
- **Frontend Example**: `frontend_example.html`

## Testing

Run the test to verify HTML generation:
```bash
.venv/Scripts/python.exe test_html_generation.py
```

Open the frontend example in a browser:
```bash
# Open frontend_example.html in your browser
# Make sure the FastAPI server is running on localhost:8000
```

## Error Handling

All endpoints properly handle errors:

**404 - Report Not Found**
```json
{
  "detail": "Report not found"
}
```

**400 - Invalid Request**
```json
{
  "detail": "Topic cannot be empty"
}
```

**500 - Server Error**
```json
{
  "detail": "Failed to process markdown file: ..."
}
```

## Security

✅ Path sanitization with `os.path.basename()`
✅ File type validation (.md, .pdf only)
✅ Consistent REPORTS_DIR usage
✅ No directory traversal vulnerabilities
✅ Proper error messages without exposing internals

## Notes

- HTML generation happens automatically during report creation
- If HTML generation fails, it logs a warning but doesn't fail the request
- The `report_html` field will be present in all successful responses
- PDF generation is independent and also gracefully handled
- All file paths use proper sanitization to prevent security issues
