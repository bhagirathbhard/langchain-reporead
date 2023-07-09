# Repository Reader using Langchain and OpenAI

This repository provides a set of tools and scripts that leverage Langchain and OpenAI to read and analyze the content of a repository.
[Langchain User Docs: Analysis of Twitter the-algorithm source code with LangChain, GPT4, and Deep Lake](https://python.langchain.com/docs/use_cases/code/twitter-the-algorithm-analysis-deeplake)

## Added Features

This repo extends on to the use case documentation above with the following new features -

- `questions.txt` - This file can be used to store questions separated by a comma `,`. This way the code file does not have to be altered.

- `answerX.md` - The code creates individual answers.md file within the answers folder so that the output from the LLM is clear and can be used for various purposes independently.

## Prerequisites

Before using this repository reader, make sure you have the following prerequisites:

- Python 3.7 or higher
- OpenAI API key: Obtain an API key from OpenAI and set it as an environment variable named `OPENAI_API_KEY`.
- ActiveLoop API key: Sign up for ActiveLoop and obtain an API key. Set it as an environment variable named `ACTIVE_LOOP_API_KEY`.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/bhagirathbhard/langchain-reporead.git
   cd langchain_reporead

2. Install dependencies through poetry

    ```bash
    poetry install

3. Activate poetry shell
    ```bash
    poetry shell

This step is necessary to ensure that the repository reader scripts and tools are executed within the Poetry environment.
