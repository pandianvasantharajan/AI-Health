# AI Health UI

React frontend application for the AI Health Service.

## Coming Soon

This React application will provide a user interface for:

- File upload functionality
- Integration with the AI Health Service API
- User-friendly file management

## Planned Features

- **File Upload Interface**: Drag-and-drop file upload
- **PDF Validation**: Client-side PDF file validation
- **Upload Progress**: Real-time upload progress indication
- **File Management**: View uploaded files and manage them
- **Responsive Design**: Mobile-friendly interface

## Future Setup

```bash
# Navigate to the UI directory
cd ai-health-ui

# Install dependencies
npm install

# Start development server
npm start
```

## Integration

The React app will integrate with the AI Health Service API endpoints:

- `POST /upload/pdf` - Upload PDF files
- `POST /upload/file` - Upload any file type
- `GET /health` - Service health check
- `GET /file/{bucket_name}/{file_key}` - Get file URLs

Stay tuned for the complete implementation!