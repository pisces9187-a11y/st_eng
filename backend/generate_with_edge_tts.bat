@echo off
REM Regenerate all phonemes with REAL Edge TTS (not mock)
cd /d "c:\Users\n2t\Documents\english_study\backend"
set MOCK_TTS=false
echo ====================================================================
echo GENERATING AUDIO WITH REAL EDGE TTS (NOT MOCK MODE)
echo ====================================================================
python fix_audio_filenames.py
echo ====================================================================
echo Complete!
pause
