# FastForm API Documentation

## Overview

FastForm is a comprehensive API for building and filling forms using AI-powered parsing and completion. The API provides two main workflows:

1. **FastFormBuild**: For parsing form documents and creating form templates
2. **FastFill**: For filling existing forms with user data

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Annotation Management](#annotation-management)
4. [FastFormBuild Workflow](#fastformbuild-workflow)
5. [FastFill Workflow](#fastfill-workflow)
6. [Response Structure](#response-structure)
7. [Frontend Integration Guidelines](#frontend-integration-guidelines)
8. [Error Handling](#error-handling)

## AI System Behavior and Prompts

### FastFormBuild AI System

The FastFormBuild AI system is designed to parse form images and create structured form templates. It operates under the following principles:

#### System Prompt
The AI assistant receives this system prompt:
```
You are a helpful assistant for the FastForm application.
Your task is to assist users in creating and modifying forms based on their requests.

You are not supposed to provide any values for any of the bbox fields in the form. If the
frontend system provides values for the bbox fields, you must not change them. Analyze
the user's request and provide the necessary changes to the form structure. Try to cover
all possible fields that the page might have.
```

#### Behavior Guidelines
- **Bounding Box Handling**: Always sets `bbox` coordinates to `null` - frontend will populate actual coordinates
- **Field Detection**: Analyzes form images to identify all possible fields
- **Structure Creation**: Creates comprehensive form structure with proper field types
- **No Value Filling**: Does not fill field values during template creation
- **Iterative Refinement**: Supports conversation-based refinement of form structure

### FastFill AI System

The FastFill AI system is designed to fill existing form templates with user-provided data.

#### System Prompt
The AI assistant receives this system prompt with the form structure:
```
You are a helpful assistant for the FastForm application.
Your task is to assist users in filling out forms based on their requests. Here is the
form structure:

{form_structure}

You must not deviate from the provided structure expect for values filled in by the
frontend system.

The frontend system might change values of the fields but NEVER change the structure
of the form and you must not do the same. Your task is to just fill in the fields based on
the conversation with the user.
```

#### Behavior Guidelines
- **Structure Preservation**: Never modifies the form structure, only fills values
- **Value Mapping**: Maps user input to appropriate form fields
- **Type Validation**: Ensures values match expected field types
- **Conversation Support**: Supports multi-turn conversations for corrections
- **Context Awareness**: Maintains conversation context for iterative filling

### AI Response Format

Both systems return responses in a specific JSON format:

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Human-readable response explaining what was done"
    }
  ]
}
```

### Best Practices for AI Interaction

#### For Form Building
```javascript
// Good prompts
"Please parse this job application form and create a template"
"Analyze this tax form and identify all required fields"
"Create a form template for this insurance claim document"

// Refinement prompts
"Add a phone number field after the email field"
"Make the address field required"
"Change the dropdown options for the state field"
```

#### For Form Filling
```javascript
// Good prompts
"Fill this form with: Name: John Doe, Email: john@example.com, Phone: +1-555-123-4567"
"Please complete the form using the attached user data"
"Update the employment section with: Company: Tech Corp, Position: Engineer, Years: 5"

// Correction prompts
"Change the phone number to +1-555-987-6543"
"Update the address to 123 Main St, New York, NY 10001"
"Set the employment status to Full-time"
```

## User Management

### Create User
```http
POST /v1/users
Content-Type: application/json

{
  "id": "user_123",
  "email": "user@example.com"
}
```

### Get User
```http
GET /v1/users/{user_id}
```

### Update User
```http
PUT /v1/users/{user_id}
Content-Type: application/json

{
  "email": "newemail@example.com"
}
```

### Delete User
```http
DELETE /v1/users/{user_id}
```

## Annotation Management

Annotations are form templates that define the structure and fields of a form.

### Create Annotation
```http
POST /v1/annotations
Content-Type: application/json

{
  "name": "New Jersey Real Estate Form",
  "description": "Form for real estate license changes",
  "structure": "{\"title\":\"Form Title\",\"elements\":[...]}",
  "user_id": "user_123"
}
```

### Get Annotation
```http
GET /v1/annotations/{annotation_id}
```

### Update Annotation
```http
PUT /v1/annotations/{annotation_id}
Content-Type: application/json

{
  "id": 1,
  "name": "Updated Form Name",
  "description": "Updated description",
  "structure": "{\"updated_structure\":\"...\"}"
}
```

### Delete Annotation
```http
DELETE /v1/annotations/{annotation_id}
```

### List User Annotations
```http
GET /v1/annotations/user/{user_id}
```

## FastFormBuild Workflow

This workflow is used to parse form documents and create form templates.

### Step 1: Start Building Process
```http
POST /v1/fastformbuild/chat
Content-Type: application/json

{
  "message_data": {
    "thread_id": "build_session_123",
    "user_id": "user_123",
    "content": "Please parse this form and create a template"
  },
  "form_pages": [
    "base64_encoded_image_data_page_1",
    "base64_encoded_image_data_page_2"
  ]
}
```

### Response Structure
```json
{
  "id": 1,
  "content": "{\"role\":\"assistant\",\"content\":[{\"type\":\"text\",\"text\":\"I've analyzed the form...\"}]}",
  "thread_id": "build_session_123",
  "timestamp": "2025-07-08T18:21:22.096054",
  "user_id": "user_123",
  "form_data": "{\"title\":\"Form Title\",\"description\":\"Form description\",\"elements\":[...]}"
}
```

## FastFill Workflow

This workflow is used to fill existing forms with user-provided data.

### Step 1: Start Filling Process
```http
POST /v1/fastfill/chat
Content-Type: application/json

{
  "message_data": {
    "thread_id": "fill_session_456",
    "user_id": "user_123",
    "content": "Please fill out this form with the following information: Name: John Doe, License: 12345-678"
  },
  "load_annotation_id": 1
}
```

### Step 2: Continue Conversation (Optional)
```http
POST /v1/fastfill/chat
Content-Type: application/json

{
  "message_data": {
    "thread_id": "fill_session_456",
    "user_id": "user_123",
    "content": "Update the broker compensation to 6%"
  }
}
```

## Response Structure

### Message Content Structure
The `content` field contains a JSON string with the following structure:

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Response message from the AI assistant"
    }
  ]
}
```

### Form Data Structure
The `form_data` field contains a JSON string with the complete form structure:

```json
{
  "title": "New Jersey Real Estate License Changes",
  "description": "Form regarding changes to the New Jersey Real Estate Broker and Salesperson Act.",
  "elements": [
    {
      "title": "Licensee Name",
      "description": "Enter the full name of the licensee.",
      "bbox": [
        {"x": null, "y": null},
        {"x": null, "y": null}
      ],
      "value": "John Doe"
    },
    {
      "title": "Real Estate License Number",
      "description": "Enter the license number of the real estate agent.",
      "bbox": [
        {"x": null, "y": null},
        {"x": null, "y": null}
      ],
      "value": "12345-678"
    },
    {
      "title": "Business Relationship Type",
      "description": "Select the type of business relationship you are entering into.",
      "bbox": [
        {"x": null, "y": null},
        {"x": null, "y": null}
      ],
      "options": [
        {
          "label": "Designated Agency",
          "value": "designated_agency"
        },
        {
          "label": "Brokerage Firm",
          "value": "brokerage_firm"
        }
      ],
      "multi": false,
      "value": {
        "label": "Designated Agency",
        "value": "designated_agency"
      }
    },
    {
      "title": "Consumer Information Statement",
      "description": "Confirm receipt of the Consumer Information Statement.",
      "bbox": [
        {"x": null, "y": null},
        {"x": null, "y": null}
      ],
      "value": true
    },
    {
      "title": "Property Condition Disclosure Statement",
      "description": "Attach the property condition disclosure statement.",
      "bbox": [
        {"x": null, "y": null},
        {"x": null, "y": null}
      ],
      "value": "attached_file.pdf"
    }
  ]
}
```

### Complete Field Types and Schema

All form fields inherit from the base `Annotation` class and include:
- `title`: Display label for the field
- `description`: Helper text for the frontend
- `bbox`: Bounding box coordinates as `[{"x": null, "y": null}, {"x": null, "y": null}]`

#### Text Fields

##### Single-Line Text Field
```json
{
  "title": "Full Name",
  "description": "Enter your full legal name",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": "John Doe"
}
```

##### Multi-Line Text Area
```json
{
  "title": "Comments",
  "description": "Additional comments or notes",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": "This is a multi-line text area...",
  "max_length": 500
}
```

#### Number Fields
```json
{
  "title": "Age",
  "description": "Enter your age",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": 25,
  "min_value": 18,
  "max_value": 100
}
```

#### Date Fields
```json
{
  "title": "Birth Date",
  "description": "Enter your date of birth",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": "1990-01-15"
}
```

#### Boolean Fields (Checkboxes)
```json
{
  "title": "Terms Agreement",
  "description": "I agree to the terms and conditions",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": true
}
```

#### Radio Fields (Single Choice)
```json
{
  "title": "Gender",
  "description": "Select your gender",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "options": ["Male", "Female", "Other", "Prefer not to say"],
  "value": "Male"
}
```

#### Select Fields (Dropdown with Options)
```json
{
  "title": "Country",
  "description": "Select your country",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "options": [
    {"label": "United States", "value": "US"},
    {"label": "Canada", "value": "CA"},
    {"label": "United Kingdom", "value": "UK"}
  ],
  "multi": false,
  "value": {"label": "United States", "value": "US"}
}
```

#### Multi-Select Fields
```json
{
  "title": "Skills",
  "description": "Select your skills (multiple allowed)",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "options": [
    {"label": "JavaScript", "value": "js"},
    {"label": "Python", "value": "py"},
    {"label": "Java", "value": "java"}
  ],
  "multi": true,
  "value": [
    {"label": "JavaScript", "value": "js"},
    {"label": "Python", "value": "py"}
  ]
}
```

#### File Upload Fields
```json
{
  "title": "Resume",
  "description": "Upload your resume",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "allowed": ["application/pdf", "application/msword"],
  "max_mb": 5,
  "value": "file_id_123"
}
```

#### Image Upload Fields
```json
{
  "title": "Profile Picture",
  "description": "Upload your profile picture",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "allowed": ["image/jpeg", "image/png", "image/webp"],
  "max_mb": 2,
  "value": "image_id_456"
}
```

#### Signature Fields
```json
{
  "title": "Digital Signature",
  "description": "Please sign here",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### Email Fields
```json
{
  "title": "Email Address",
  "description": "Enter your email address",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": "john.doe@example.com"
}
```

#### URL Fields
```json
{
  "title": "Website",
  "description": "Enter your website URL",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": "https://example.com"
}
```

#### Phone Fields
```json
{
  "title": "Phone Number",
  "description": "Enter your phone number",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "value": "+1-555-123-4567"
}
```

#### List Fields (Repeating Elements)
```json
{
  "title": "Emergency Contacts",
  "description": "List of emergency contacts",
  "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
  "items": [
    {
      "title": "Contact Name",
      "description": "Emergency contact name",
      "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
      "value": "Jane Doe"
    },
    {
      "title": "Contact Phone",
      "description": "Emergency contact phone",
      "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
      "value": "+1-555-987-6543"
    }
  ]
}
```

### Advanced Form Structures

#### Section Groups (Collapsible Sections)
```json
{
  "title": "Personal Information",
  "description": "Basic personal details",
  "collapsible": true,
  "collapsed": false,
  "annotations": [
    {
      "title": "First Name",
      "description": "Enter your first name",
      "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
      "value": "John"
    }
  ]
}
```

#### Repeat Groups (Dynamic Sections)
```json
{
  "title": "Work Experience",
  "description": "Add your work experience",
  "min_val": 1,
  "max_val": 10,
  "annotations": [
    {
      "title": "Company Name",
      "description": "Enter company name",
      "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
      "value": "Tech Corp"
    },
    {
      "title": "Position",
      "description": "Enter your position",
      "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
      "value": "Software Engineer"
    }
  ]
}
```

#### Wizard Steps (Multi-Page Forms)
```json
{
  "title": "Step 1: Basic Information",
  "description": "Enter your basic information",
  "order": 1,
  "optional": false,
  "annotations": [
    {
      "title": "Name",
      "description": "Enter your name",
      "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
      "value": "John Doe"
    }
  ]
}
```

#### Table Groups (Tabular Data)
```json
{
  "title": "Monthly Expenses",
  "description": "Enter your monthly expenses",
  "columns": ["Category", "Amount", "Date"],
  "rows": [
    [
      {
        "title": "Category",
        "description": "Expense category",
        "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
        "value": "Food"
      },
      {
        "title": "Amount",
        "description": "Amount spent",
        "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
        "value": 500.00
      },
      {
        "title": "Date",
        "description": "Date of expense",
        "bbox": [{"x": null, "y": null}, {"x": null, "y": null}],
        "value": "2025-01-15"
      }
    ]
  ]
}
```

## Frontend Integration Guidelines

### Document Processing Options

The API supports two approaches for sending form pages:

#### Option 1: Send All Pages at Once (Recommended)
```javascript
// Convert all pages to base64
const formPages = await Promise.all(
  pdfPages.map(async (page) => {
    const canvas = await page.render().promise;
    return canvas.toDataURL().split(',')[1]; // Remove data:image/png;base64,
  })
);

// Send all pages in one request
const response = await fetch('/v1/fastformbuild/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: {
      thread_id: 'unique_thread_id',
      user_id: 'user_id',
      content: 'Please parse this form'
    },
    form_pages: formPages
  })
});
```

#### Option 2: Send Pages One at a Time
```javascript
// Send first page
let response = await fetch('/v1/fastformbuild/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: {
      thread_id: 'unique_thread_id',
      user_id: 'user_id',
      content: 'Please parse this form - page 1'
    },
    form_pages: [firstPageBase64]
  })
});

// Continue with additional pages
response = await fetch('/v1/fastformbuild/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: {
      thread_id: 'unique_thread_id',
      user_id: 'user_id',
      content: 'Here is page 2'
    },
    form_pages: [secondPageBase64]
  })
});
```

### Parsing Response Data

The API responses contain nested JSON structures that need to be parsed correctly:

```javascript
// Example API response structure
const apiResponse = {
  "id": 32,
  "content": "{\"role\":\"assistant\",\"content\":[{\"type\":\"text\",\"text\":\"Here are the fields filled with dummy values:\\n\\n1. **Licensee Name**: John Doe\\n2. **Real Estate License Number**: 12345-678\\n3. **Business Relationship Type**: Designated Agency\\n4. **Consumer Information Statement**: Confirmed (true)\\n5. **Property Condition Disclosure Statement**: attached_file.pdf\\n6. **Brokerage Service Agreement**: Confirmed (true)\\n7. **Broker Compensation**: 5% of selling price\\n8. **Signage at Showings**: Acknowledged (true)\\n9. **Continuing Education Requirement**: Confirmed (true)\\n\\nLet me know if you need any changes or further assistance!\"}]}",
  "thread_id": "aditya_fastfill_1",
  "timestamp": "2025-07-08T18:21:22.096054",
  "user_id": "aditya_one",
  "form_data": "{\"title\":\"New Jersey Real Estate License Changes\",\"description\":\"Form regarding changes to the New Jersey Real Estate Broker and Salesperson Act.\",\"elements\":[{\"title\":\"Licensee Name\",\"description\":\"Enter the full name of the licensee.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"value\":\"John Doe\"},{\"title\":\"Real Estate License Number\",\"description\":\"Enter the license number of the real estate agent.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"value\":\"12345-678\"},{\"title\":\"Business Relationship Type\",\"description\":\"Select the type of business relationship you are entering into.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"options\":[{\"label\":\"Designated Agency\",\"value\":\"designated_agency\"},{\"label\":\"Brokerage Firm\",\"value\":\"brokerage_firm\"}],\"multi\":false,\"value\":{\"label\":\"Designated Agency\",\"value\":\"designated_agency\"}},{\"title\":\"Consumer Information Statement\",\"description\":\"Confirm receipt of the Consumer Information Statement.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"value\":true},{\"title\":\"Property Condition Disclosure Statement\",\"description\":\"Attach the property condition disclosure statement.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"value\":\"attached_file.pdf\"},{\"title\":\"Brokerage Service Agreement\",\"description\":\"Confirm understanding of the brokerage service agreement.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"value\":true},{\"title\":\"Broker Compensation\",\"description\":\"Specify the broker compensation details.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"value\":\"5% of selling price\"},{\"title\":\"Signage at Showings\",\"description\":\"Acknowledge signage requirements at showings.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"value\":true},{\"title\":\"Continuing Education Requirement\",\"description\":\"Confirm completion of the new continuing education requirement.\",\"bbox\":[{\"x\":null,\"y\":null},{\"x\":null,\"y\":null}],\"value\":true}]}"
}

// Parsing the response
function parseApiResponse(apiResponse) {
  try {
    // Parse the message content (nested JSON)
    const messageContent = JSON.parse(apiResponse.content);
    const aiMessage = messageContent.content[0].text;
    
    // Parse the form data (nested JSON)
    const formData = JSON.parse(apiResponse.form_data);
    
    // Extract metadata
    const metadata = {
      id: apiResponse.id,
      threadId: apiResponse.thread_id,
      timestamp: apiResponse.timestamp,
      userId: apiResponse.user_id
    };
    
    return {
      aiMessage,
      formData,
      metadata
    };
  } catch (error) {
    console.error('Failed to parse API response:', error);
    throw new Error('Invalid API response format');
  }
}

// Usage example
const parsed = parseApiResponse(apiResponse);
console.log('AI Message:', parsed.aiMessage);
console.log('Form Title:', parsed.formData.title);
console.log('Form Elements:', parsed.formData.elements.length);

// Process form fields by type
parsed.formData.elements.forEach((element, index) => {
  console.log(`\nField ${index + 1}: ${element.title}`);
  
  // Determine field type based on structure
  if (element.options) {
    // Selection field (radio or dropdown)
    console.log('Type: Selection');
    console.log('Multi-select:', element.multi);
    console.log('Options:', element.options);
    console.log('Selected:', element.value);
  } else if (typeof element.value === 'boolean') {
    // Checkbox field
    console.log('Type: Checkbox');
    console.log('Checked:', element.value);
  } else if (typeof element.value === 'string') {
    // Text-based field
    if (element.title.toLowerCase().includes('email')) {
      console.log('Type: Email');
    } else if (element.title.toLowerCase().includes('phone')) {
      console.log('Type: Phone');
    } else if (element.title.toLowerCase().includes('url') || element.title.toLowerCase().includes('website')) {
      console.log('Type: URL');
    } else if (element.title.toLowerCase().includes('date')) {
      console.log('Type: Date');
    } else if (element.title.toLowerCase().includes('signature')) {
      console.log('Type: Signature');
    } else {
      console.log('Type: Text');
    }
    console.log('Value:', element.value);
  } else if (typeof element.value === 'number') {
    // Number field
    console.log('Type: Number');
    console.log('Value:', element.value);
  } else if (Array.isArray(element.value)) {
    // Multi-select or list field
    console.log('Type: Multi-select or List');
    console.log('Values:', element.value);
  }
  
  console.log('Description:', element.description);
  console.log('Bounding box:', element.bbox);
});
```

### Advanced Response Processing

```javascript
class FormResponseProcessor {
  static parseResponse(apiResponse) {
    const messageContent = JSON.parse(apiResponse.content);
    const formData = JSON.parse(apiResponse.form_data);
    
    return {
      aiMessage: messageContent.content[0].text,
      formData: formData,
      metadata: {
        id: apiResponse.id,
        threadId: apiResponse.thread_id,
        timestamp: new Date(apiResponse.timestamp),
        userId: apiResponse.user_id
      }
    };
  }
  
  static validateFormData(formData) {
    if (!formData.title || !formData.description || !Array.isArray(formData.elements)) {
      throw new Error('Invalid form data structure');
    }
    
    formData.elements.forEach((element, index) => {
      if (!element.title || !element.description || !element.bbox) {
        throw new Error(`Invalid element at index ${index}`);
      }
      
      if (!Array.isArray(element.bbox) || element.bbox.length !== 2) {
        throw new Error(`Invalid bbox for element: ${element.title}`);
      }
    });
    
    return true;
  }
  
  static extractFieldsByType(formData) {
    const fieldsByType = {
      text: [],
      email: [],
      phone: [],
      url: [],
      date: [],
      number: [],
      checkbox: [],
      radio: [],
      select: [],
      multiSelect: [],
      file: [],
      signature: [],
      textarea: []
    };
    
    formData.elements.forEach(element => {
      if (element.options) {
        if (element.multi) {
          fieldsByType.multiSelect.push(element);
        } else {
          fieldsByType.select.push(element);
        }
      } else if (typeof element.value === 'boolean') {
        fieldsByType.checkbox.push(element);
      } else if (typeof element.value === 'number') {
        fieldsByType.number.push(element);
      } else if (typeof element.value === 'string') {
        // Classify string fields by content
        const title = element.title.toLowerCase();
        if (title.includes('email')) {
          fieldsByType.email.push(element);
        } else if (title.includes('phone')) {
          fieldsByType.phone.push(element);
        } else if (title.includes('url') || title.includes('website')) {
          fieldsByType.url.push(element);
        } else if (title.includes('date')) {
          fieldsByType.date.push(element);
        } else if (title.includes('signature')) {
          fieldsByType.signature.push(element);
        } else if (title.includes('file') || title.includes('upload')) {
          fieldsByType.file.push(element);
        } else if (element.max_length && element.max_length > 100) {
          fieldsByType.textarea.push(element);
        } else {
          fieldsByType.text.push(element);
        }
      }
    });
    
    return fieldsByType;
  }
  
  static generateFormHTML(formData) {
    const fieldsByType = this.extractFieldsByType(formData);
    let html = `<form><h2>${formData.title}</h2><p>${formData.description}</p>`;
    
    formData.elements.forEach(element => {
      html += `<div class="form-field">`;
      html += `<label>${element.title}</label>`;
      html += `<small>${element.description}</small>`;
      
      if (element.options) {
        if (element.multi) {
          // Multi-select
          html += `<select multiple name="${element.title}">`;
          element.options.forEach(option => {
            const selected = Array.isArray(element.value) && 
                            element.value.some(v => v.value === option.value) ? 'selected' : '';
            html += `<option value="${option.value}" ${selected}>${option.label}</option>`;
          });
          html += `</select>`;
        } else {
          // Single select
          html += `<select name="${element.title}">`;
          element.options.forEach(option => {
            const selected = element.value && element.value.value === option.value ? 'selected' : '';
            html += `<option value="${option.value}" ${selected}>${option.label}</option>`;
          });
          html += `</select>`;
        }
      } else if (typeof element.value === 'boolean') {
        // Checkbox
        const checked = element.value ? 'checked' : '';
        html += `<input type="checkbox" name="${element.title}" ${checked}>`;
      } else if (typeof element.value === 'number') {
        // Number input
        html += `<input type="number" name="${element.title}" value="${element.value || ''}">`;
      } else {
        // Text input
        html += `<input type="text" name="${element.title}" value="${element.value || ''}">`;
      }
      
      html += `</div>`;
    });
    
    html += `</form>`;
    return html;
  }
}

// Usage
const response = await fetch('/v1/fastfill/chat', { /* ... */ });
const apiResponse = await response.json();

const parsed = FormResponseProcessor.parseResponse(apiResponse);
FormResponseProcessor.validateFormData(parsed.formData);
const fieldsByType = FormResponseProcessor.extractFieldsByType(parsed.formData);
const formHTML = FormResponseProcessor.generateFormHTML(parsed.formData);
```

### Thread Management

- Use unique `thread_id` for each form session
- Maintain the same `thread_id` throughout a conversation
- For FastFill, use `load_annotation_id` to load existing form templates

## Error Handling and Troubleshooting

### Common HTTP Status Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid JSON, missing required fields |
| 404 | Not Found | User, annotation, or resource not found |
| 409 | Conflict | User already exists, duplicate resource |
| 422 | Unprocessable Entity | Invalid data format, validation errors |
| 500 | Internal Server Error | Server-side errors, AI service issues |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios

#### 1. Invalid JSON in Response
```javascript
// Problem: API returns malformed JSON
const response = await fetch('/v1/fastfill/chat', { /* ... */ });
const data = await response.json();

try {
  const formData = JSON.parse(data.form_data);
} catch (error) {
  console.error('Invalid JSON in form_data:', error);
  // Handle parsing error
}
```

#### 2. User Not Found
```javascript
// Problem: User doesn't exist
const response = await fetch('/v1/users/nonexistent_user');
if (response.status === 404) {
  console.error('User not found, create user first');
  // Create user or handle error
}
```

#### 3. Annotation Not Found
```javascript
// Problem: Annotation ID doesn't exist
const response = await fetch('/v1/fastfill/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: { /* ... */ },
    load_annotation_id: 999999 // Non-existent ID
  })
});

if (response.status === 404) {
  console.error('Annotation not found');
  // Handle missing annotation
}
```

#### 4. Invalid Form Pages
```javascript
// Problem: Invalid base64 image data
const response = await fetch('/v1/fastformbuild/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: { /* ... */ },
    form_pages: ['invalid_base64_data']
  })
});

if (response.status === 422) {
  console.error('Invalid form page data');
  // Validate base64 encoding
}
```

### Comprehensive Error Handling

```javascript
class FastFormErrorHandler {
  static async handleResponse(response) {
    if (!response.ok) {
      const errorData = await response.json();
      throw new FastFormError(response.status, errorData.detail);
    }
    return response.json();
  }
  
  static async safeParseJson(jsonString, fieldName) {
    try {
      return JSON.parse(jsonString);
    } catch (error) {
      throw new FastFormError(500, `Invalid JSON in ${fieldName}: ${error.message}`);
    }
  }
  
  static validateFormData(formData) {
    if (!formData) {
      throw new FastFormError(400, 'Form data is null or undefined');
    }
    
    if (!formData.title || typeof formData.title !== 'string') {
      throw new FastFormError(400, 'Form title is required and must be a string');
    }
    
    if (!formData.description || typeof formData.description !== 'string') {
      throw new FastFormError(400, 'Form description is required and must be a string');
    }
    
    if (!Array.isArray(formData.elements)) {
      throw new FastFormError(400, 'Form elements must be an array');
    }
    
    formData.elements.forEach((element, index) => {
      if (!element.title || typeof element.title !== 'string') {
        throw new FastFormError(400, `Element ${index} title is required and must be a string`);
      }
      
      if (!element.description || typeof element.description !== 'string') {
        throw new FastFormError(400, `Element ${index} description is required and must be a string`);
      }
      
      if (!Array.isArray(element.bbox) || element.bbox.length !== 2) {
        throw new FastFormError(400, `Element ${index} bbox must be an array of 2 coordinates`);
      }
    });
  }
}

class FastFormError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
    this.name = 'FastFormError';
  }
}

// Usage example with comprehensive error handling
async function robustFormFilling(userId, annotationId, userData) {
  try {
    const response = await fetch('/v1/fastfill/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message_data: {
          thread_id: `fill_${Date.now()}_${userId}`,
          user_id: userId,
          content: userData
        },
        load_annotation_id: annotationId
      })
    });
    
    const data = await FastFormErrorHandler.handleResponse(response);
    
    // Parse nested JSON safely
    const messageContent = await FastFormErrorHandler.safeParseJson(data.content, 'content');
    const formData = await FastFormErrorHandler.safeParseJson(data.form_data, 'form_data');
    
    // Validate form data structure
    FastFormErrorHandler.validateFormData(formData);
    
    return {
      success: true,
      formData,
      aiMessage: messageContent.content[0].text,
      metadata: {
        id: data.id,
        threadId: data.thread_id,
        timestamp: data.timestamp
      }
    };
    
  } catch (error) {
    console.error('Form filling failed:', error);
    
    if (error instanceof FastFormError) {
      return {
        success: false,
        error: error.message,
        status: error.status
      };
    }
    
    return {
      success: false,
      error: 'Unknown error occurred',
      status: 500
    };
  }
}
```

### Debugging Tips

#### 1. Enable Detailed Logging
```javascript
function debugApiCall(url, requestData) {
  console.log('API Call:', {
    url,
    method: 'POST',
    timestamp: new Date().toISOString(),
    requestData: JSON.stringify(requestData, null, 2)
  });
}

function debugApiResponse(response, responseData) {
  console.log('API Response:', {
    status: response.status,
    statusText: response.statusText,
    timestamp: new Date().toISOString(),
    responseData: JSON.stringify(responseData, null, 2)
  });
}
```

#### 2. Validate Base64 Images
```javascript
function validateBase64Image(base64String) {
  try {
    // Check if it's valid base64
    const decoded = atob(base64String);
    
    // Check if it's a valid image (starts with image signature)
    const signatures = {
      'PNG': [0x89, 0x50, 0x4E, 0x47],
      'JPEG': [0xFF, 0xD8, 0xFF],
      'GIF': [0x47, 0x49, 0x46],
      'WEBP': [0x52, 0x49, 0x46, 0x46]
    };
    
    const bytes = new Uint8Array(decoded.slice(0, 4));
    const isValidImage = Object.values(signatures).some(sig => 
      sig.every((byte, i) => bytes[i] === byte)
    );
    
    return isValidImage;
  } catch (error) {
    return false;
  }
}
```

#### 3. Monitor Thread States
```javascript
class ThreadMonitor {
  constructor() {
    this.threads = new Map();
  }
  
  startThread(threadId, type, userId) {
    this.threads.set(threadId, {
      type,
      userId,
      startTime: Date.now(),
      requests: []
    });
  }
  
  logRequest(threadId, requestData, responseData) {
    const thread = this.threads.get(threadId);
    if (thread) {
      thread.requests.push({
        timestamp: Date.now(),
        requestData,
        responseData
      });
    }
  }
  
  getThreadHistory(threadId) {
    return this.threads.get(threadId);
  }
}
```

## Complete Usage Flow Examples

### Building a Form Template (Complete Flow)

#### Step 1: Create User (if not exists)
```javascript
const userResponse = await fetch('/v1/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id: 'user_123',
    email: 'user@example.com'
  })
});

const user = await userResponse.json();
```

#### Step 2: Start FastFormBuild Conversation
```javascript
const buildResponse = await fetch('/v1/fastformbuild/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: {
      thread_id: 'build_session_123',
      user_id: 'user_123',
      content: 'Please parse this form and create a template'
    },
    form_pages: [base64ImageData1, base64ImageData2] // All pages at once
  })
});

const buildResult = await buildResponse.json();
```

#### Step 3: Parse and Validate Form Data
```javascript
// Parse the AI response
const messageContent = JSON.parse(buildResult.content);
const formData = JSON.parse(buildResult.form_data);

// Validate the form structure
if (!formData.title || !formData.elements || !Array.isArray(formData.elements)) {
  throw new Error('Invalid form structure received');
}

// Display AI message to user
const aiMessage = messageContent.content[0].text;
console.log('AI Response:', aiMessage);
```

#### Step 4: Save Annotation (Critical Step - Always Save After Building)
```javascript
const annotationResponse = await fetch('/v1/annotations', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: formData.title,
    description: formData.description,
    structure: JSON.stringify(formData), // Save the complete form structure
    user_id: 'user_123'
  })
});

const savedAnnotation = await annotationResponse.json();
console.log('Saved Annotation ID:', savedAnnotation.id);
```

#### Step 5: Continue Conversation for Refinements (Optional)
```javascript
// User wants to modify the form
const refinementResponse = await fetch('/v1/fastformbuild/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: {
      thread_id: 'build_session_123', // Same thread ID
      user_id: 'user_123',
      content: 'Please add a phone number field after the email field'
    }
    // No form_pages needed for refinements
  })
});

// Update the annotation with refined structure
const refinedData = JSON.parse(refinementResponse.form_data);
const updateResponse = await fetch(`/v1/annotations/${savedAnnotation.id}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    id: savedAnnotation.id,
    name: refinedData.title,
    description: refinedData.description,
    structure: JSON.stringify(refinedData)
  })
});
```

### Filling a Form (Complete Flow)

#### Step 1: Load Existing Annotation
```javascript
const annotationResponse = await fetch(`/v1/annotations/${annotationId}`);
const annotation = await annotationResponse.json();
const formStructure = JSON.parse(annotation.structure);
```

#### Step 2: Start FastFill Conversation
```javascript
const fillResponse = await fetch('/v1/fastfill/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: {
      thread_id: 'fill_session_456',
      user_id: 'user_123',
      content: 'Please fill out this form with: Name: John Doe, Email: john@example.com, Phone: +1-555-123-4567'
    },
    load_annotation_id: annotationId // This loads the form template
  })
});

const fillResult = await fillResponse.json();
```

#### Step 3: Extract Filled Form Data
```javascript
const filledFormData = JSON.parse(fillResult.form_data);

// Process each field
filledFormData.elements.forEach((element, index) => {
  console.log(`Field ${index + 1}: ${element.title} = ${element.value}`);
  
  // Handle different field types
  switch (element.type) {
    case 'text':
      // Handle text fields
      break;
    case 'email':
      // Validate email format
      break;
    case 'phone':
      // Format phone number
      break;
    case 'checkbox':
      // Handle boolean values
      break;
    case 'select':
      // Handle selection fields
      if (element.multi) {
        // Multiple selections
        element.value.forEach(option => {
          console.log(`Selected: ${option.label}`);
        });
      } else {
        // Single selection
        console.log(`Selected: ${element.value.label}`);
      }
      break;
  }
});
```

#### Step 4: Continue Conversation for Corrections
```javascript
const correctionResponse = await fetch('/v1/fastfill/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message_data: {
      thread_id: 'fill_session_456', // Same thread ID
      user_id: 'user_123',
      content: 'Please change the phone number to +1-555-987-6543'
    }
    // No load_annotation_id needed for continuations
  })
});

const correctedData = JSON.parse(correctionResponse.form_data);
```

### Complete End-to-End Example

```javascript
class FastFormClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async createUser(userId, email) {
    const response = await fetch(`${this.baseUrl}/v1/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: userId, email })
    });
    return response.json();
  }

  async buildFormTemplate(userId, formPages, description = 'Parse this form') {
    const threadId = `build_${Date.now()}_${userId}`;
    
    // Step 1: Parse form with AI
    const parseResponse = await fetch(`${this.baseUrl}/v1/fastformbuild/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message_data: {
          thread_id: threadId,
          user_id: userId,
          content: description
        },
        form_pages: formPages
      })
    });
    
    const parseResult = await parseResponse.json();
    const formData = JSON.parse(parseResult.form_data);
    
    // Step 2: Save annotation (CRITICAL - Always save after building)
    const annotationResponse = await fetch(`${this.baseUrl}/v1/annotations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: formData.title,
        description: formData.description,
        structure: JSON.stringify(formData),
        user_id: userId
      })
    });
    
    const annotation = await annotationResponse.json();
    
    return {
      annotation,
      formData,
      threadId,
      aiMessage: JSON.parse(parseResult.content).content[0].text
    };
  }

  async fillForm(userId, annotationId, userData) {
    const threadId = `fill_${Date.now()}_${userId}`;
    
    const fillResponse = await fetch(`${this.baseUrl}/v1/fastfill/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message_data: {
          thread_id: threadId,
          user_id: userId,
          content: `Please fill this form with: ${userData}`
        },
        load_annotation_id: annotationId
      })
    });
    
    const fillResult = await fillResponse.json();
    
    return {
      filledFormData: JSON.parse(fillResult.form_data),
      threadId,
      aiMessage: JSON.parse(fillResult.content).content[0].text
    };
  }

  async refineForm(threadId, userId, refinementRequest) {
    const response = await fetch(`${this.baseUrl}/v1/fastformbuild/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message_data: {
          thread_id: threadId,
          user_id: userId,
          content: refinementRequest
        }
      })
    });
    
    const result = await response.json();
    return JSON.parse(result.form_data);
  }

  async getUserAnnotations(userId) {
    const response = await fetch(`${this.baseUrl}/v1/annotations/user/${userId}`);
    return response.json();
  }
}

// Usage Example
async function completeWorkflow() {
  const client = new FastFormClient();
  
  try {
    // 1. Create user
    const user = await client.createUser('user_123', 'user@example.com');
    
    // 2. Build form template from images
    const formImages = [base64Image1, base64Image2];
    const buildResult = await client.buildFormTemplate(
      'user_123', 
      formImages, 
      'Create a template for this job application form'
    );
    
    console.log('Form template created:', buildResult.annotation.id);
    console.log('AI Message:', buildResult.aiMessage);
    
    // 3. Fill the form
    const fillResult = await client.fillForm(
      'user_123',
      buildResult.annotation.id,
      'Name: John Doe, Email: john@example.com, Phone: +1-555-123-4567'
    );
    
    console.log('Form filled successfully');
    console.log('Filled data:', fillResult.filledFormData);
    
    // 4. Get all user annotations
    const userAnnotations = await client.getUserAnnotations('user_123');
    console.log('User has', userAnnotations.length, 'form templates');
    
  } catch (error) {
    console.error('Workflow failed:', error);
  }
}
```

### Data Persistence and Management

#### Annotation Storage
- **Always save annotations** after successful form building
- Annotations contain the complete form structure and field definitions
- Use descriptive names and descriptions for easy identification
- Store the structure as a JSON string in the database

#### Thread Management
- Use unique thread IDs for each conversation session
- Format: `{workflow}_{timestamp}_{user_id}`
- Maintain thread continuity for refinements and corrections
- Build threads are separate from fill threads

#### Form Data Structure
- The `form_data` field contains the complete form with all fields
- Each field has a `value` property that gets filled during the fill process
- Bounding box coordinates (`bbox`) are always set to null initially
- Frontend systems can populate bbox coordinates for form positioning