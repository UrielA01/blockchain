# Blockchain Project

This project is a minimal blockchain implementation in Python. It allows the creation of a decentralized network of nodes that can communicate, validate transactions, and mine blocks. The project uses Flask for the networking layer and includes Docker for easier deployment.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Docker Setup](#docker-setup)
- [API Reference](#api-reference)
- [Contribution](#contribution)
- [License](#license)

## Overview

This project demonstrates a basic blockchain implementation with a peer-to-peer network. It includes the following components:
- A distributed ledger where transactions are recorded.
- Nodes that communicate with each other using Flask APIs.
- Basic transaction validation and mining mechanism.
- UTXO (Unspent Transaction Output) model for managing transaction outputs.

## Features

- **Blockchain**: Add new blocks to the blockchain and broadcast them across nodes.
- **Peer-to-Peer Communication**: Nodes can discover and communicate with each other.
- **Transaction Handling**: Sign, validate, and broadcast transactions across the network.
- **Mining**: Basic mining functionality for adding blocks.
- **Docker Setup**: Easily set up a multi-node environment using Docker Compose.

## Installation

### Prerequisites
Make sure you have the following installed:
- Python 3.x
- Virtualenv (optional, but recommended)
- Docker (optional, for containerized setup)

### Step 1: Clone the Repository
```bash
git clone https://github.com/UrielA01/blockchain.git
cd blockchain
```

### Step 2: Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/MacOS
# or
venv\Scripts\activate     # For Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage
### Running the Blockchain
To run the server, navigate to the project root and use the following command:
```bash
export PYTHONPATH=$(pwd)
python src/server.py 
```
### Running in Multiple Nodes
You can run multiple instances of the node on different ports. Use the following command:
```bash
python src/server --port 5001
```

## Docker Setup
You can easily run the project in Docker using Docker Compose.
## Step 1: Build Docker Images
```bash
docker-compose build
```
## Step 2: Start the Nodes
```bash
docker-compose up
```
This will create a network with four nodes.


## API Reference

#### Get chain

```http
  GET /chain
```

#### Get known nodes

```http
  GET /known_nodes
```

#### Mine new block from current transactions

```http
  POST /mine
```

#### Send block

```http
  POST /block
```

| Parameter | Type    | Description                               |
|:----------|:--------|:------------------------------------------|
| `block`   | `Block` | **Required**. The block being broadcast |

#### Send transaction

```http
  POST /transaction
```

| Parameter     | Type          | Description                                   |
|:--------------|:--------------|:----------------------------------------------|
| `transaction` | `Transaction` | **Required**. The transaction being broadcast |

#### Advertise new block in the network

```http
  POST /advertise
```

| Parameter | Type   | Description                    |
|:----------|:-------|:-------------------------------|
| `node`    | `Node` | **Required**. Advertised block |

## Contribution
Feel free to fork this project and create pull requests. Contributions are welcome!

### Steps to Contribute:
1. Fork the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Commit your changes (git commit -m "Add new feature").
4. Push to the branch (git push origin feature-branch).
5. Open a pull request.

## License
This project is open-source and available under the MIT License.

This README provides an overview, setup instructions, 
and usage details. 
You can extend or customize it as your project evolves. 
Let me know if you'd like to add any specific sections!
