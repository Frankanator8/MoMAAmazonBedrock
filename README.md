# Amazon x Columbia
### **Technical Documentation: TransparaFetch**

This document outlines the implementation of a healthcare price transparency assistant. The system's long-term vision is to provide broad access to healthcare cost information. The current implementation serves as a Minimum Viable Product (MVP) with an initial scope focused on hospitals within Rhode Island.

### **System Overview: The Implementation**

The system is designed to provide users with clear and personalized information about healthcare costs. For the MVP, it leverages a powerful language model, a comprehensive knowledge base covering Rhode Island hospitals, and precise computational functions to deliver accurate price estimates. The core of the system is a Bedrock Agent that acts as an intelligent orchestrator, managing user interactions and data retrieval.

### **Core Components**

*   **Bedrock Agent:** As the central component, this agent processes user requests and acts as the "orchestrator" for the entire process. It is powered by the **AWS Nova Pro** model, which was selected to balance response speed and quality. For the MVP, its knowledge base is populated with hospital price lists and insurance policies for over 15 hospitals in Rhode Island.

*   **Lambda Management:** To ensure precision and prevent model-generated errors (hallucinations) in critical areas, specific tasks like savings calculations and price comparisons are delegated to an AWS Lambda function. This provides reliable, accurate computations.

*   **Prompt Engineering (Security):** Carefully designed prompts and instructions guide the agent's behavior. This ensures that its responses are helpful, accurate, and secure, and that it operates within its defined capabilities.

*   **Challenge: Lambda Integration:** A key technical challenge in this implementation is the seamless and robust integration of the Lambda function with the Bedrock Agent.

### **Technical Architecture**

The system employs a modern, scalable architecture:

1.  **Frontend (Next.js):** A user-facing web application built with Next.js serves as the primary interface. The chat-style user interface is implemented using **assistantUI** components.

2.  **Bedrock:** The core agent that receives requests from the frontend. It interprets the user's needs and coordinates with the knowledge base and Lambda functions to formulate a response.

3.  **Knowledge Base (S3):** The Bedrock agent is connected to a knowledge base stored in an Amazon S3 bucket. For the MVP, this knowledge base, named `moma-knowledge-base`, contains hospital pricing and health insurance information for Rhode Island.

4.  **Lambda Function:** A Python-based Lambda function is used for specialized tasks requiring precise computation, such as cost calculations and price comparisons. The interaction with this function is managed through an action group named `HealthcareCostCalculator`.

### **Instructions for the Agent (MVP)**

The Bedrock Agent for the MVP is governed by a specific set of instructions that define its current capabilities and operational boundaries:

*   **MVP Scope:** The agent's functionality is currently limited to serving as a healthcare price transparency assistant for hospitals in Rhode Island.

*   **Capabilities:**
    1.  Search and summarize price transparency documents from the MVP knowledge base.
    2.  Explain medical terminology and insurance concepts in simple terms.
    3.  Calculate personalized out-of-pocket costs based on a patient's deductible and insurance information.
    4.  Compare prices across different hospitals within Rhode Island to help patients find the best value.

*   **Important Guidelines:**
    *   The agent must only provide information about Rhode Island hospitals. If asked about hospitals in other states, it should politely inform the user that the current version is focused on Rhode Island.
    *   Medical jargon should be explained clearly using everyday language.
    *   When providing price information, the source hospital must always be cited.
    *   For all cost calculations and price comparisons, the agent **must** use the designated Lambda functions (`calculateOutOfPocketCost` and `comparePrices`) via the action group. It is strictly prohibited from performing these calculations itself.
    *   The agent should be helpful, accurate, and empathetic, recognizing the stressful nature of healthcare costs.
    *   **For debugging purposes,** if the Lambda function is used for cost calculations or price comparisons, the agent's response **must** include the word "LAMBDA" to confirm that the function was invoked.