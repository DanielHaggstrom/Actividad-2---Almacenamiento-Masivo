# Distributed Storage Simulator

This repository contains an old academic assignment that simulates a very simple distributed file system (DFS) in Python. The project is not a production storage system: everything runs in memory inside one process, but it is useful for understanding how a master node can coordinate file partitioning, replica placement, integrity checks, and simple MapReduce-style analysis over stored text.

The command names, comments, and most messages are in Spanish because the original activity was written in Spanish.

## What the activity is about

The assignment models a storage cluster with:

- one master node that keeps metadata and coordinates operations
- many slave nodes that store file blocks
- several strategies for distributing blocks across the cluster
- optional replication to tolerate simulated node failure
- simple data analysis commands executed with a Map/Reduce pattern

At a high level, the workflow is:

1. A local text file is loaded from disk with `escribir`.
2. The master splits it into fixed-size payload blocks.
3. Each block receives metadata so it can be reconstructed later.
4. The blocks are distributed across slave nodes according to the selected write strategy.
5. `leer` gathers the matching blocks from the slaves, sorts them, removes duplicates created by replication, and rebuilds the original text.

## Repository contents

- `DFSim.py`: command-line entry point. It creates the simulated cluster and exposes the available commands.
- `Master.py`: master-node logic, metadata handling, block creation, block placement, integrity checks, and MapReduce orchestration.
- `Slave.py`: slave-node logic for storing, reading, erasing, mapping, and reducing blocks.
- `texto`, `texto2`, `texto3`, `texto4`, `texto-copy`, `texto-copy2`, `celestina`: sample input files you can load into the simulator.

## How the simulator works

### Cluster configuration

The simulator starts with these constants from `DFSim.py`:

- `5000` slave nodes
- `4096` characters of memory per slave
- `256` characters per stored block

All storage is in memory. Nothing written into the simulator survives after the program exits.

### File storage model

When you store a file:

- the master reads the source file from the local filesystem
- the file is split into payload chunks of `250` characters (`256` block size minus `6` characters of metadata)
- every chunk gets a compact header containing:
  - a one-character file identifier
  - a per-block sequence identifier
  - an encoded block length

Those metadata fields let the master reconstruct the original file order during `leer`.

### Replication

The third argument of `escribir` is the number of extra replicas, not the total number of copies.

- `0` means one stored copy
- `1` means two total copies
- `2` means three total copies

This detail matters because the code internally adds `1` to the user-provided value.

### Simulated faults

`Slave.write()` includes a very small random failure probability (`1e-8`). When triggered, the entire contents of that slave are cleared. That is why the project includes integrity-check and rebuild commands.

## Write strategies

`escribir` accepts four placement modes. You can use either the full name or the short letter shown below.

- `hasta_maxima_carga` / `a`: fill one slave as much as possible before moving to the next.
- `secuencial` / `b`: make a single ordered pass across the slaves, placing at most one block on each node during that pass.
- `aleatorio` / `c`: place each block on a random slave with available space.
- `primero_vacio` / `d`: prioritize the slaves with the most free capacity first.

## Available commands

These are the commands actually exposed by `DFSim.py`:

- `escribir <modo> <archivo> <replicas>`: load a local text file into the simulated DFS.
- `leer <archivo>`: reconstruct and print a stored file.
- `borrar <archivo>`: remove all blocks belonging to a stored file.
- `comprobar`: print the defect ratio for every stored file.
- `restablecer`: erase and write every stored file again, then reset the integrity counter.
- `contar_caracteres <archivo>`: count character frequencies with a Map/Reduce flow.
- `contar_pares <archivo>`: count two-character pairs with a Map/Reduce flow.
- `listar_palabras <archivo>`: return words that appear exactly once, sorted by length.
- `debug`: print the raw contents of the simulated nodes plus master metadata.
- `ayuda`: print the built-in help text.
- `salir`: exit the simulator.

## Running it

The project has no third-party dependencies. A normal Python installation is enough.

On Windows:

```powershell
py DFSim.py
```

The committed `venv/` directory is old and currently points to a missing interpreter, so it should not be relied on. If you want an isolated environment, create a fresh virtual environment instead of using the bundled one.

## Example session

```text
[DFSim]>> escribir a texto3 0
Datos guardados.

[DFSim]>> leer texto3
...file contents...

[DFSim]>> contar_caracteres texto3
{'0': 23, '1': 23, ...}

[DFSim]>> comprobar
El ratio de defectos de texto3 es 0.0

[DFSim]>> borrar texto3
Archivo borrado
```

## Important limitations and quirks

- This is a simulation, not a persistent storage system.
- The CLI parser is a plain space split, so file names with spaces are not supported.
- `comprobar` prints results directly instead of returning a formatted report string.
- `listar_palabras` does not list all words with counts; it only returns words whose final count is `1`.
- `restablecer` rewrites files using mode `a` in the current implementation, even though one comment in `Master.py` says "secuencial".
- The source files contain some old encoding issues in comments and messages, but the simulator still runs.
- The built-in `ayuda` text has minor spelling inconsistencies. The command list above reflects the real implementation.

## Sample data

The repository includes several text files for quick experiments:

- `texto3` is a very small input useful for quick smoke tests.
- `texto4` is a medium-size lorem ipsum sample.
- `texto`, `texto-copy`, and `texto-copy2` are larger stress-test style inputs.
- `celestina` is a Project Gutenberg text and is not original project code.

## License

This repository is licensed under the MIT License for the source code in this project. See `LICENSE` for the full text.

Bundled sample texts may have their own copyright or distribution terms. In particular, `celestina` includes Project Gutenberg copyright notices and should be treated according to the terms embedded in that file.
