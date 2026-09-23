# Recovery and validation

The previous `/mnt/data/mosfet-amplifier-github.zip` was unavailable in the current desktop environment. This is a newly reconstructed package from the five recovered conversation attachments, not a byte-for-byte recovery of the missing generated ZIP.

The original project ZIP passed Python zipfile CRC validation. Its complete original bytes are preserved under originals/. Active project files were copied from its top-level project. Only four Sim.Library paths were changed in the active schematic, from an absolute Downloads path to models/nmos_t.txt. Circuit values, project configuration, and workbook analysis settings were not altered. Local locks, preferences, and historical backups are retained only inside the original ZIP.

Both PDFs and model files were copied byte-for-byte. The report and guidelines were inspected by text extraction. No simulation, KiCad GUI opening, electrical-rule check, or PCB validation was performed.

The rebuilt ZIP was checked for CRC errors, extracted into a fresh directory, and every extracted file was compared byte-for-byte to the staged package. A SHA-256 checksum accompanies the downloadable ZIP.

## Repository presentation update

The README and supporting guides were expanded, three historical report figures were extracted, and a Python package verifier was added. Original design files, PDFs, models, and archive are unchanged. The checksum manifest was regenerated for this edition. No new circuit simulations were run.

## v0.2.0 verification update

After the original recovery, fresh ngspice runs were completed. See docs/VERIFICATION.md and simulations/README.md. Earlier statements about no simulations describe the recovery stage only. The original schematic and models remain unchanged; the experimental variant is separate.
