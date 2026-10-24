# Additive packaging correction

Version 0.1.0-draft.2 corrects a publication integrity mismatch in the Git source tree for 0.1.0-draft.1 at commit 8a3b8cf91b2630a744311dc4bd984a6f4e53dc73. The dependency_tasks_fictional.csv fixture was normalized from CRLF to LF by the text publication path, while the manifest described its original CRLF bytes.

The prior manifest described 479 bytes and SHA-256 1b9e2396fe7cb7adef896d275c2c21caf7084c3d95547d45b129a8adf15c3011. The publicly fetched source member contained 473 bytes and SHA-256 c225e0b180408752191b054fb9df97742a015660002d985d3a9b47b04f8d0fd3. A fresh public-source pickup found the mismatch. The other checked members matched.

This version intentionally uses LF text before generating the manifest and ZIP, so published source and archive describe the same bytes. Prior source commit and ZIP history remain available. This is a packaging correction, not a functional fix or independent human acceptance claim. The CSV-BARE-QUOTE parser defect remains. No new browser test result is claimed.
