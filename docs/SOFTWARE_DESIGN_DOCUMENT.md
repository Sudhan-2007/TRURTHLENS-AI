# SOFTWARE DESIGN DOCUMENT (SDD)
## TruthLens AI

### AI-Powered News Credibility and Fake News Detection System

**Document Type:** Software Design Document
**Project:** TruthLens AI
**Version:** 1.0
**Date:** August 2026

---

# 1. Introduction

## 1.1 Purpose

This Software Design Document describes the technical design and architecture of **TruthLens AI**, an AI-powered system designed to help users evaluate the credibility of online news and identify potentially misleading, false, or unverified information.

The system analyzes news content using Artificial Intelligence, Natural Language Processing, source analysis, and evidence-based verification techniques. Instead of providing only a "Fake" or "Real" classification, TruthLens AI is designed to provide a credibility assessment together with supporting reasons and evidence.

The purpose of this document is to explain how the system components interact and how the proposed functionality can be implemented.

---

## 1.2 Scope

TruthLens AI is designed to accept news information from users in different forms, such as:

* News article text
* News headlines
* News URLs
* Uploaded content
* Images containing news information, if image analysis is enabled

The system processes the submitted information and generates:

* Extracted claims
* Source information
* Supporting evidence
* Contradicting evidence
* Credibility score
* Final assessment
* Explanation of the assessment
* Verification status

The system is intended to assist users in making better decisions before believing or sharing online information.

---

# 2. Design Goals

The primary design goals of TruthLens AI are:

1. **Accuracy**
   Provide reliable credibility assessments based on available evidence.

2. **Explainability**
   Explain why a particular result was generated.

3. **Transparency**
   Allow users to understand the verification process.

4. **Usability**
   Provide a simple interface that can be used by non-technical users.

5. **Scalability**
   Allow additional verification sources and AI models to be added later.

6. **Security**
   Protect user information and prevent unauthorized access.

7. **Extensibility**
   Support future features such as multilingual verification, image analysis, and browser extensions.

---

# 3. System Overview

The overall system follows the following workflow:

```text
                    USER
                      |
                      v
              +---------------+
              | TruthLens UI   |
              +-------+-------+
                      |
                      v
              +---------------+
              | Input Handler |
              +-------+-------+
                      |
                      v
              +---------------+
              | Text / Claim   |
              | Extraction     |
              +-------+-------+
                      |
          +-----------+-----------+
          |                       |
          v                       v
 +----------------+      +----------------+
 | AI/NLP Analysis|      | Source Analysis|
 +--------+-------+      +--------+-------+
          |                       |
          +-----------+-----------+
                      |
                      v
              +---------------+
              | Evidence      |
              | Verification  |
              +-------+-------+
                      |
                      v
              +---------------+
              | Credibility   |
              | Engine        |
              +-------+-------+
                      |
                      v
              +---------------+
              | Explanation   |
              | Generator     |
              +-------+-------+
                      |
                      v
              +---------------+
              | Result /      |
              | Evidence Card |
              +---------------+
                      |
                      v
                    USER
```

---

# 4. System Architecture

TruthLens AI follows a modular layered architecture.

## 4.1 Presentation Layer

The presentation layer provides interaction between the user and the system.

Responsibilities:

* Accept news input
* Accept URLs
* Display analysis status
* Display credibility score
* Display verification result
* Display evidence
* Display explanations
* Display source information

Possible technologies:

* HTML
* CSS
* JavaScript
* React or another frontend framework

---

## 4.2 Application Layer

The application layer controls the overall business logic.

Responsibilities:

* Receive user requests
* Validate input
* Coordinate analysis modules
* Manage verification workflow
* Generate final response
* Communicate with database and external services

Possible technologies:

* Python
* Flask
* FastAPI
* Node.js

---

## 4.3 AI/NLP Layer

The AI layer analyzes the linguistic and semantic characteristics of news content.

Responsibilities include:

* Text preprocessing
* Tokenization
* Feature extraction
* Claim extraction
* Semantic analysis
* Classification
* Sentiment analysis where required
* Detection of suspicious linguistic patterns

Possible technologies:

* Python
* Scikit-learn
* Transformers
* BERT-based models
* NLP libraries

---

## 4.4 Evidence Verification Layer

This layer is responsible for finding and comparing external evidence.

Responsibilities:

* Search for related claims
* Identify supporting sources
* Identify contradicting sources
* Compare information
* Determine evidence strength
* Provide source references

The system should prioritize authoritative and independent sources where possible.

---

## 4.5 Credibility Engine

The credibility engine combines multiple signals rather than depending on a single AI prediction.

Example signals:

```text
AI classification
       +
Source credibility
       +
Evidence agreement
       +
Contradicting evidence
       +
Content characteristics
       +
Information freshness
       |
       v
Credibility Score
```

The exact weighting should be determined through testing and validation.

---

# 5. Major System Modules

## 5.1 User Management Module

Responsibilities:

* User registration
* Login
* Authentication
* User profile management
* Analysis history

If authentication is not required in the current implementation, this module can be treated as optional.

---

## 5.2 News Input Module

The module allows users to submit information for verification.

Supported inputs may include:

* Headline
* Article text
* URL
* Image

Input validation should check:

* Empty input
* Invalid URL
* Unsupported file format
* Excessive input size
* Malformed content

---

## 5.3 Content Extraction Module

When the user provides a URL, the system extracts relevant information from the webpage.

Possible information:

* Article title
* Main article text
* Author
* Publisher
* Publication date
* Images
* Metadata

The system should remove unnecessary webpage elements such as advertisements and navigation content where possible.

---

# 6. Claim Extraction Module

The system identifies factual claims from the submitted content.

For example:

**Article:**

> "The government announced a new scholarship program providing ₹50,000 to every college student."

The system may extract:

**Claim:**

> "The government announced a ₹50,000 scholarship for every college student."

The claim then becomes the primary unit for verification.

This approach is preferable to treating an entire article as one indivisible claim.

---

# 7. AI Analysis Module

The AI module evaluates the submitted content.

## 7.1 Text Preprocessing

Processing may include:

* Cleaning HTML
* Removing unnecessary characters
* Normalization
* Tokenization
* Stop-word processing where appropriate
* Text encoding

## 7.2 Feature Analysis

Potential features include:

* Linguistic patterns
* Semantic representation
* Headline characteristics
* Sensational language
* Repetition
* Claim structure
* Contextual relationships

## 7.3 Classification

The AI model generates a classification or probability.

Example:

```text
Likely Reliable     0.82
Unverified          0.10
Likely Misleading   0.06
Likely False        0.02
```

The final system result should not depend solely on this probability.

---

# 8. Source Credibility Module

The source analysis module evaluates the origin of the information.

Potential factors:

* Publisher identity
* Domain information
* Author information
* Publication history
* Availability of contact/about information
* Source reputation
* Presence of supporting references
* Consistency with authoritative sources

The system should avoid automatically declaring an entire domain "fake" based on a single article.

---

# 9. Evidence Verification Module

This module searches for evidence related to extracted claims.

## 9.1 Supporting Evidence

Sources that agree with or support the claim are identified.

## 9.2 Contradicting Evidence

Sources that provide information inconsistent with the claim are identified.

## 9.3 Evidence Strength

Evidence can be categorized as:

* Strong
* Moderate
* Weak
* Insufficient

The system should also consider the quality and independence of sources.

---

# 10. Credibility Scoring

TruthLens AI generates an overall credibility assessment using multiple signals.

A conceptual model is:

```text
Credibility Score =
    AI Analysis
    + Source Reliability
    + Supporting Evidence
    - Contradicting Evidence
    + Freshness
    + Claim Consistency
```

The exact formula and weights should be determined experimentally.

Example result:

```text
Credibility Score: 78/100

Assessment:
LIKELY RELIABLE

Evidence:
3 supporting sources
1 neutral source
0 major contradictions
```

The score should always be accompanied by an explanation.

---

# 11. Result Classification

The system can use the following categories:

| Score  | Classification         |
| ------ | ---------------------- |
| 80–100 | Highly Reliable        |
| 60–79  | Likely Reliable        |
| 40–59  | Unverified             |
| 20–39  | Potentially Misleading |
| 0–19   | Likely False           |

These thresholds should be adjusted after evaluation of the actual system.

---

# 12. Explainability Module

The Explainability Module is one of the most important components of TruthLens AI.

Instead of returning only:

> "Fake News"

the system should explain the result.

Example:

```text
Assessment: Potentially Misleading

Reasons:

1. The main claim could not be confirmed
   by an authoritative source.

2. Two independent sources provide
   contradictory information.

3. The original article provides
   insufficient supporting evidence.

4. The headline uses highly sensational
   wording.
```

This allows users to understand the reasoning behind the result.

---

# 13. Evidence Card

TruthLens AI should provide a concise evidence summary.

Example:

```text
+--------------------------------------+
|          TRUTHLENS AI                |
+--------------------------------------+
| Assessment: Potentially Misleading   |
| Confidence: 84%                      |
+--------------------------------------+
| Supporting Sources: 1                |
| Contradicting Sources: 3             |
| Official Confirmation: Not Found     |
+--------------------------------------+
| Why?                                 |
| The claim could not be independently |
| verified and is contradicted by      |
| multiple reliable sources.           |
+--------------------------------------+
| [View Evidence] [View Sources]       |
+--------------------------------------+
```

---

# 14. Database Design

A relational or document-oriented database may be used.

## 14.1 Users Table

| Field         | Type     | Description               |
| ------------- | -------- | ------------------------- |
| user_id       | Integer  | Unique user ID            |
| name          | String   | User name                 |
| email         | String   | User email                |
| password_hash | String   | Encrypted/hashed password |
| created_at    | DateTime | Account creation date     |

---

## 14.2 Analysis Table

| Field          | Type     | Description                 |
| -------------- | -------- | --------------------------- |
| analysis_id    | Integer  | Unique analysis ID          |
| user_id        | Integer  | User who submitted content  |
| input_type     | String   | Text/URL/Image              |
| input_content  | Text     | Submitted content/reference |
| score          | Float    | Credibility score           |
| classification | String   | Final assessment            |
| created_at     | DateTime | Analysis time               |

---

## 14.3 Claims Table

| Field       | Type    | Description              |
| ----------- | ------- | ------------------------ |
| claim_id    | Integer | Unique claim ID          |
| analysis_id | Integer | Related analysis         |
| claim_text  | Text    | Extracted claim          |
| status      | String  | Verified/Unverified/etc. |
| confidence  | Float   | Claim confidence         |

---

## 14.4 Sources Table

| Field         | Type    | Description                   |
| ------------- | ------- | ----------------------------- |
| source_id     | Integer | Unique source ID              |
| claim_id      | Integer | Related claim                 |
| source_name   | String  | Publisher name                |
| source_url    | Text    | Source reference              |
| source_type   | String  | Official/News/Fact-check/etc. |
| evidence_type | String  | Supporting/Contradicting      |
| reliability   | Float   | Source reliability            |

---

# 15. API Design

The backend may expose REST APIs.

## 15.1 Analyze News

```text
POST /api/analyze
```

Request:

```json
{
  "content": "News article text",
  "type": "text"
}
```

Response:

```json
{
  "score": 78,
  "classification": "Likely Reliable",
  "confidence": 0.86,
  "claims": [],
  "supporting_sources": [],
  "contradicting_sources": [],
  "explanation": []
}
```

---

## 15.2 Analyze URL

```text
POST /api/analyze-url
```

Request:

```json
{
  "url": "https://example.com/news"
}
```

The backend extracts the article and sends it through the analysis pipeline.

---

## 15.3 Analysis History

```text
GET /api/history
```

Returns previous analyses associated with the authenticated user.

---

# 16. User Interface Design

The TruthLens interface should be simple and understandable.

## 16.1 Home Page

Components:

* TruthLens AI logo
* Short explanation
* News text input
* URL input
* Upload option if supported
* Analyze button

Example:

```text
          TRUTHLENS AI

      Verify Before You Share

 [ Paste news article or URL here ]

             [ ANALYZE ]

  "Don't trust the AI. Check the evidence."
```

---

## 16.2 Analysis Result Page

The result page should contain:

1. Overall assessment
2. Credibility score
3. Confidence level
4. Extracted claims
5. Supporting evidence
6. Contradicting evidence
7. Source information
8. Explanation
9. Verification timestamp

---

# 17. Transparency Design

A key design principle is:

> **TruthLens AI should not ask users to blindly trust the AI. It should help users evaluate the evidence.**

The interface should provide a **"How did TruthLens decide?"** option.

Possible workflow:

```text
How did TruthLens decide?
          |
          v
Claim extracted
          |
          v
Sources searched
          |
          v
Evidence compared
          |
          v
Source credibility evaluated
          |
          v
AI assessment generated
          |
          v
Final result
```

---

# 18. Security Design

Security mechanisms should include:

* Password hashing
* Secure authentication
* Authorization
* Input validation
* HTTPS
* API authentication
* Rate limiting
* Secure database access
* Protection against SQL injection
* Protection against XSS
* Protection against malicious URLs
* File validation for uploaded content

User data should not be exposed unnecessarily.

---

# 19. Error Handling

The system should gracefully handle failures.

Examples:

### Invalid URL

```text
Unable to analyze this URL.
Please provide a valid public webpage.
```

### Insufficient Evidence

```text
TruthLens could not find sufficient reliable
evidence to verify this claim.
```

The system should classify this as **Unverified**, rather than automatically calling the news false.

### External Source Failure

```text
Some verification sources are currently
unavailable. The result may have limited
confidence.
```

### AI Model Failure

The application should return a controlled error instead of exposing internal system details.

---

# 20. Performance Requirements

The system should aim to:

* Return basic analysis within an acceptable response time.
* Handle multiple users concurrently.
* Cache repeated requests where appropriate.
* Avoid unnecessary external API calls.
* Process large articles efficiently.
* Scale independently between frontend and backend services.

Actual response-time targets should be defined according to the deployed infrastructure.

---

# 21. Reliability and Availability

TruthLens AI should:

* Handle temporary external API failures.
* Prevent a single unavailable source from stopping the entire analysis.
* Maintain analysis records where appropriate.
* Provide meaningful fallback messages.
* Log system errors for debugging.

---

# 22. Privacy Requirements

The system should follow privacy-by-design principles.

Important considerations:

* Collect only necessary user information.
* Avoid storing sensitive article content unnecessarily.
* Clearly communicate data retention policies.
* Allow deletion of user history where applicable.
* Protect stored credentials.
* Avoid exposing user-submitted content to unauthorized users.

---

# 23. Logging and Monitoring

The system should record operational events such as:

* Login attempts
* Analysis requests
* API failures
* Model errors
* External source failures
* Response times
* System exceptions

Sensitive information should not be unnecessarily included in logs.

---

# 24. Testing Strategy

Testing should include:

## Unit Testing

Test individual components:

* URL validation
* Text preprocessing
* Claim extraction
* Score calculation
* API functions

## Integration Testing

Verify interaction between:

* Frontend and backend
* Backend and AI model
* Backend and database
* Verification service and external sources

## System Testing

Test the complete workflow:

```text
Input
 ↓
Extraction
 ↓
Claim Detection
 ↓
Evidence Search
 ↓
AI Analysis
 ↓
Scoring
 ↓
Explanation
 ↓
Result
```

## AI Model Evaluation

Use an appropriate labeled dataset and calculate metrics such as:

* Accuracy
* Precision
* Recall
* F1-score
* Confusion matrix

The evaluation dataset should be separate from the training data.

---

# 25. Trust and Explainability Requirements

Trust is a central design principle of TruthLens AI.

The system should:

1. Provide evidence for important claims.
2. Show the sources used during verification.
3. Explain the reasons behind the assessment.
4. Display uncertainty when evidence is insufficient.
5. Avoid presenting AI predictions as absolute truth.
6. Allow users to inspect source information.
7. Display when the analysis was performed.
8. Distinguish between evidence and AI-generated interpretation.

The core principle is:

> **"Don't trust the AI. Trust the evidence."**

---

# 26. Deployment Architecture

A possible deployment architecture is:

```text
                  INTERNET
                     |
                     v
              +-------------+
              | Web Client  |
              +------+------+
                     |
                     v
              +-------------+
              | API Server  |
              +------+------+
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
   AI/NLP       Verification    Database
   Service        Service
       |             |
       |             v
       |       External Sources
       |
       v
   ML Models
```

The components may be deployed separately depending on project requirements.

---

# 27. Future Enhancements

Future versions of TruthLens AI may include:

* Tamil and other regional language support
* Browser extension
* WhatsApp/Telegram verification interface where platform policies permit
* Image manipulation detection
* Deepfake analysis
* Video verification
* Voice/audio misinformation detection
* Real-time breaking-news verification
* Personalized media-literacy recommendations
* Community-driven evidence submission
* Fact-checker collaboration
* Mobile application
* Multimodal AI verification

---

# 28. Design Limitations

TruthLens AI cannot guarantee absolute truth in every situation.

Limitations may include:

* Lack of available evidence
* Conflicting sources
* Newly developing events
* Biased or incomplete sources
* AI model errors
* Incorrect source metadata
* Satirical or opinion-based content
* Limited information about newly created websites
* Difficulty verifying complex claims

Therefore, the system should communicate uncertainty rather than forcing every article into a binary true/false category.

---

# 29. Conclusion

TruthLens AI is designed as an evidence-oriented news credibility assessment platform rather than a simple fake-news classification system.

The proposed architecture combines:

```text
Artificial Intelligence
        +
Natural Language Processing
        +
Source Analysis
        +
Evidence Verification
        +
Credibility Scoring
        +
Explainable Results
```

The most important design principle is transparency. TruthLens AI should help users understand **why information may be trustworthy or suspicious**, while allowing users to inspect the evidence themselves.

The ultimate objective is not to make users blindly trust TruthLens AI, but to encourage users to **verify information before believing or sharing it**.

### Core Principle

> **TruthLens AI — Don't just trust the news. See the evidence.**
