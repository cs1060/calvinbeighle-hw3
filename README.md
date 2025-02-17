# Gnome File Organizer

A rapid prototype demonstrating AI-powered file organization, built individually using Codeium and generative AI tools. This prototype implements the primary user journey of uploading and automatically categorizing files using OpenAI's GPT model.

## Live Demo
[Demo URL: https://gnome-file-organizer.netlify.app](https://gnome-file-organizer.netlify.app)

Screenshots of the working prototype are available in the `/screenshots` directory.

## Prototype Scope & Implementation Notes
This prototype implements the core user journey from the PRD:
- Upload files via drag-and-drop or file picker interface
- AI analysis of file contents using GPT-3.5 for intelligent categorization
- Automatic organization into a logical folder hierarchy
- Support for common file types (PDFs, Word docs, CSVs, images) up to 16MB

As a rapid prototype focused on the primary user flow, some features are not yet implemented:
- File preview functionality shows "Preview not available" message
- Download feature displays "Downloads coming soon" 
- User accounts/authentication shows "Sign in feature in development"

The prototype uses synthetic test data and simulated file analysis for demonstration purposes.

## Local Development

### Prerequisites
- Python 3.8+
- OpenAI API key (for GPT-3.5 integration)
- Web browser
- Git

### Setup
1. Clone the repository:

bash
git clone https://github.com/yourusername/gnome-file-organizer.git
cd gnome-file-organizer

2. Install dependencies:

bash
pip install -r requirements.txt

3. Create a `.env` file in the root directory with your OpenAI API key:

env
OPENAI_API_KEY=your_openai_api_key

4. Run the Flask application:

bash
python app.py

5. Open your web browser and navigate to:

http://localhost:5000

Use sample files in the `/sample_files` directory for testing.

## Known Limitations
- Maximum file size: 16MB
- Limited file type support
- No persistent storage
- Single-user operation
- API rate limiting may affect organization speed

## Future Enhancements
- Multi-user support
- Persistent storage
- Advanced search capabilities
- File preview system
- Batch processing for large files

## Deployment

The application is deployed on Netlify with continuous deployment from the main branch.

### Deployment Steps
1. Fork or clone this repository
2. Connect your Netlify account to your GitHub repository
3. Configure the following environment variables in Netlify:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `REACT_APP_API_URL`: Your backend API URL
4. Deploy by pushing to the main branch

The site will automatically build and deploy when changes are pushed to the main branch. You can view deployment logs and configure additional settings in the Netlify dashboard.

Visit the live demo at [https://gnome-file-organizer.netlify.app](https://gnome-file-organizer.netlify.app)
