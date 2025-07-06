# Python-based MIPS Processor Simulator

This repository contains a Python implementation of both a **Single-cycle** and a **Pipelined** MIPS processor. Each hardware component (e.g., ALU, Register File, Control Unit, Data Memory, Instruction Memory, Cache) is represented as a Python class, interconnected similarly to their physical counterparts.

## Features

- Supports various MIPS instructions (R-type, I-type, and J-type)
- Handles pipeline hazards:
  - **Data hazards** (resolved through forwarding and stalling)
  - **Control hazards** (Branch and Jump handling)
  - **Memory hazards** (Load/Store word handling)
- Implements a simple on-chip Cache simulation
- Provides detailed cycle-by-cycle simulation output and statistics

## Project Structure
```
├── ALU.py             # Arithmetic Logic Unit implementation
├── Cache.py           # Cache memory simulation
├── ControlUnit.py     # Control signals generation
├── DataMemory.py      # Data memory with integrated cache
├── ForwardUnit.py     # Forwarding and hazard detection
├── InstMemory.py      # Instruction memory loader
├── InstParser.py      # Instruction parsing
├── Latch.py           # Pipeline latches
├── Mux.py             # Multiplexer implementations
├── RegFile.py         # Register file implementation
├── SignExtend.py      # Sign extension for immediate values
├── StatePrinter.py    # Pipeline state visualization
├── SingleCycle_MIPS.py # Single-cycle processor simulation
├── Pipelined_MIPS.py  # Pipelined processor simulation
├── BinGenerator.py    # Generates binary instruction files
├── input.bin          # Sample instructions
├── factorial.bin      # Factorial computation instructions
├── summation.bin      # Summation computation instructions
├── sort.bin           # Sorting instructions
└── README.md          # This README file
```

## Requirements
- Python 3.10 or later

## Installation
1. Clone the repository:
```bash
git clone https://github.com/Nikitak1202/MIPS.git
cd MIPS
```

2. (Optional) Generate new binary instruction files using:
```bash
python BinGenerator.py
```

## Usage

### Choosing the Program
To select a binary instruction file, uncomment the desired file and comment out the others in both `SingleCycle_MIPS.py` and `Pipelined_MIPS.py`:

```python
# Example:
# InstMemory = InstMemory("factorial.bin")
InstMemory = InstMemory("summation.bin")
# InstMemory = InstMemory("input.bin")
```

### Running the Simulations
- To run the Single-cycle processor:
```bash
python SingleCycle_MIPS.py
```

- To run the Pipelined processor:
```bash
python Pipelined_MIPS.py
```

## Output
The simulation provides detailed cycle-by-cycle logs, pipeline stages visualization, and architectural state updates (register file, memory, cache statistics).
