# GPU jobs (for the human's RTX 4050 laptop)

One self-contained script per compute-bound sweep. Each script downloads its own data, runs a
planted-key control first, saves progress every few minutes (rerun the same command to resume) and
writes one small results file to upload.

## E0029_bytes_gpu.py (B01): running keys from the big byte sources

What it does: searches all 55 unsolved pages for a page-local running key taken from the bytes
(mod 29) of the 2013 Cicada OS files 761.MP3, _560.00, 560.17 and of the 75 original Liber Primus page
images. Every ciphertext F may be an F-skip. It covers 4 cipher views, 4 polarities and 2 directions.
The lab ran the text sources on CPU; these four (59 million bytes) need the GPU.

Expected: about 60 MB download, under 2 GB GPU memory (it stops itself above 5 GB), roughly 8-12 hours
for everything; it stops starting new work after `--hours` (default 15) and can be resumed later.

### Steps (Windows, PowerShell)

1. Check the GPU is visible to PyTorch (should print `True`):

   ```powershell
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. Download the script into an empty folder (or `git pull` the repo and `cd gpu`):

   ```powershell
   mkdir $HOME\lp-gpu; cd $HOME\lp-gpu
   curl.exe -L -o E0029_bytes_gpu.py https://raw.githubusercontent.com/aergasrg/liber-primus/main/gpu/E0029_bytes_gpu.py
   ```

   (Before the pull request is merged, replace `main` with `claude/blissful-gates-2v36sv`. If the repo
   is private, `git pull` instead and run it from `gpu\`.)

3. Optional 5-minute smoke test (uses small slices, writes nothing you need to keep):

   ```powershell
   python E0029_bytes_gpu.py --quick
   del results_E0029_gpu.json
   ```

4. Keep the laptop awake and plugged in, then start the overnight run:

   ```powershell
   powercfg /change standby-timeout-ac 0
   python E0029_bytes_gpu.py --hours 15 *>&1 | Tee-Object -FilePath run.log -Append
   ```

   If it stops (reboot, sleep, Ctrl+C), run the same command again: finished units are skipped.
   If the first lines say `planted-key control FAILED`, stop and upload the results file anyway.

5. In the morning, upload `results_E0029_gpu.json` (about 1 MB) from this folder. `ALL DONE` at
   the end of `run.log` means it finished; otherwise the file still holds everything finished so far.
   `powercfg /change standby-timeout-ac 30` restores sleep.

### What the lab does with it

`python3 experiments/E0029_skip_tolerant_running_key.py import-gpu --file results_E0029_gpu.json`
then `... report`. Thresholds come from the null replicates in the same file.
