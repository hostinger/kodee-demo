# Kodee-demo: Hostinger's AI-powered chat assistant

![Hostinger Logo](/kodee.jpg)

Welcome to the Kodee-demo repository! This open-source project provides an example of how you can implement your own
LLM-based AI chat assistant like Kodee from Hostinger. Below, you will find detailed instructions on how to set up, run,
and interact with it.

## Table of contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Setup](#setup)
5. [API endpoints](#api-endpoints)

## Introduction

Kodee is an AI assistant developed by Hostinger, a web hosting company, to help users manage their websites and hosting
services effortlessly. It provides instant support, answers, and guidance across various Hostinger products and
platforms, including hPanel, Hostinger Website Builder, WordPress, VPS hosting, and more.

Kodee enhances user experience by addressing a wide range of queries, performing tasks, and even solving issues
automatically. Whether you're a beginner or an experienced webmaster, Kodee is your go-to companion for building and
maintaining a website.

You can read the whole story of how we built Kodee and find Kodee demo set up instructions in our blog
post: [How we built one of the most advanced LLM-based chat assistants: Lessons learned and tips](http://www.hostinger.com/blog/building-kodee)

## Installation steps

1. **Clone the repository:** Start by pulling the Kodee-demo repository to your local machine using Git.
2. **Set up environment variables:**
    1. Copy the .env.example file to a new file named .env in the same directory. This file contains template
       environment variables needed for the project.
    2. Obtain the necessary .env values. These may include API keys, database credentials, and other sensitive
       configurations.
    3. In this example project, **DB_HOST** is set to 'db' and **REDIS_HOST** set to 'redis' as they are the names of
       the Docker containers. You can change these values if needed.
3. **Run the setup command:** With Docker running, execute the following command in the terminal within the project
   directory. This command builds and starts the necessary Docker containers for Redis, Postgres, and the application
   itself. It also runs automatic migrations to set up your Postgres database.

    ```bash
    make setup

4. **For subsequent runs:** Once the initial setup is complete, starting the project is even simpler. Just use the
   following command:

    ```bash
    make up

This command starts all the necessary services. Your **Kodee-demo** environment should now be up and running, ready for
use.

## API endpoints

### Initialize chat session

**Endpoint**: **POST** `/api/chat/initialization`

**Example request**:

```json
{
  "user_id": "test",
  "metadata": {
    "domain_name": "hostinger.com"
  }
}
```

**Example response**:

```json
{
  "conversation_id": "7ef3715a-2f47-4a09-b108-78dd6a31ea17",
  "history": []
}
```

### Respond to chat

**Endpoint**: **POST** `/api/chat/respond`

**Example request**:

```json
{
  "user_id": "test",
  "role": "user",
  "content": "Hello",
  "chatbot_label": "chatbot"
}
```

**Example response**:

```json
{
  "conversation_id": "76f9c06b-b6ce-498e-8eb4-050c1eeaa358",
  "message": {
    "role": "assistant",
    "content": "Hello! How can I assist you today?"
  },
  "handoff": {
    "should_handoff": false
  }
}
```

### Restart chat

**Endpoint**: **POST** `/api/chat/restart`

**Example request**:

```json
{
  "user_id": "test"
}
```

**Example response**:

```json
{
  "conversation_id": "7263698e-9ff5-4bb2-b8cf-b7fa7aedbb6d",
  "history": []
}
```

### Query events

**Endpoint**: **GET** `/api/history/events?conversation_id=<conversation_id>`

**Example response**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 22,
      "conversation_id": "7263698e-9ff5-4bb2-b8cf-b7fa7aedbb6d",
      "event_type": "user",
      "payload": {
        "content": {
          "role": "user",
          "content": "Hello"
        }
      },
      "message_part_id": "test-a8f5995c-f244-4f71-9f53-77287f463d14",
      "created_at": "2024-09-15T15:01:13.748932"
    },
    {
      "id": 23,
      "conversation_id": "7263698e-9ff5-4bb2-b8cf-b7fa7aedbb6d",
      "event_type": "cs_chatbot_label",
      "payload": {
        "content": {
          "message": "Setting active chatbot label for conversation",
          "label": "out_of_scope"
        }
      },
      "message_part_id": "test-5f864306-65f3-4fd7-890d-f8ed59d84b72",
      "created_at": "2024-09-15T15:01:15.279001"
    },
    {
      "id": 24,
      "conversation_id": "7263698e-9ff5-4bb2-b8cf-b7fa7aedbb6d",
      "event_type": "assistant",
      "payload": {
        "content": {
          "status": "success",
          "message": "Hello! How can I assist you today?",
          "chatbot_label": "out_of_scope_bot"
        }
      },
      "message_part_id": "test-5f864306-65f3-4fd7-890d-f8ed59d84b72",
      "created_at": "2024-09-15T15:01:15.908485"
    }
  ]
}
```

### Query messages

**Endpoint**: **GET** `/api/history/messages?conversation_id=<conversation_id>`

**Example response**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 14,
      "conversation_id": "7263698e-9ff5-4bb2-b8cf-b7fa7aedbb6d",
      "author_type": "user",
      "message": "Hello",
      "chatbot_label": "chatbot",
      "message_part_id": "test-a8f5995c-f244-4f71-9f53-77287f463d14",
      "created_at": "2024-09-15T15:01:13.752007"
    },
    {
      "id": 15,
      "conversation_id": "7263698e-9ff5-4bb2-b8cf-b7fa7aedbb6d",
      "author_type": "assistant",
      "message": "Hello! How can I assist you today?",
      "chatbot_label": "out_of_scope_bot",
      "message_part_id": "test-5f864306-65f3-4fd7-890d-f8ed59d84b72",
      "created_at": "2024-09-15T15:01:15.910829"
    }
  ]
}
```

