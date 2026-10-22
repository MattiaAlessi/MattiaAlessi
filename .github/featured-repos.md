<!--
Source rows for the "$ find ~/projects -type f -name \"featured*\"" block of README.md.

Keep the column alignment by hand (visible name = 22 chars, language = 11 chars)
and use the placeholder below to get the live star count:

    {{ index .github.repositories "<repo-name>" "stars" }}

The daily workflow (.github/workflows/update-repo-stars.yml) replaces every
placeholder with the real number of stars and rewrites the block in README.md.
-->

[01] <a href="https://github.com/MattiaAlessi/phantom-keylogger"><code>phantom-keylogger</code></a>     HTML       ★ {{ index .github.repositories "phantom-keylogger" "stars" }}    keystroke & screen capture · security research
[02] <a href="https://github.com/MattiaAlessi/Narrator"><code>Narrator</code></a>              Python     ★ {{ index .github.repositories "Narrator" "stars" }}    local TTS GUI for Kokoro-82M, voice cloning
[03] <a href="https://github.com/MattiaAlessi/miningflow"><code>miningflow</code></a>            TypeScript ★ {{ index .github.repositories "miningflow" "stars" }}    data mining & workflow tool
[04] <a href="https://github.com/MattiaAlessi/tictactoe-ai"><code>tictactoe-ai</code></a>          Python     ★ {{ index .github.repositories "tictactoe-ai" "stars" }}    neural network tic-tac-toe agent (PyTorch)
