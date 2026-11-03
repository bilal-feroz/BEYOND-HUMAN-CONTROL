# Temporary voiceover for the animatic: Windows SAPI (Microsoft Zira), one WAV per line.
# Final VO replaces these files in 08_audio/vo/final/ with the same names.
param([string]$Root = (Resolve-Path "$PSScriptRoot\..\.."))
Add-Type -AssemblyName System.Speech
$lines = @(
  @("V01", "Three hundred milliseconds."),
  @("V02", "About the time it takes you to blink."),
  @("V03", "Four machines see the same moment."),
  @("V04", "None of them sees all of it."),
  @("V05", "So they tell each other what they know..."),
  @("V06", "...and how sure they are."),
  @("V07", "The obvious choice is the closest machine."),
  @("V08", "The wave makes it the wrong one."),
  @("V09", "No one could decide this fast."),
  @("V10", "So we spend years deciding how they should.")
)
$out = Join-Path $Root "08_audio\vo\temp"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(48000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
foreach ($l in $lines) {
  $s = New-Object System.Speech.Synthesis.SpeechSynthesizer
  $s.SelectVoice("Microsoft Zira Desktop")
  $s.Rate = -2
  $f = Join-Path $out ($l[0] + ".wav")
  $s.SetOutputToWaveFile($f, $fmt)
  $s.Speak($l[1])
  $s.Dispose()
  Write-Output ("{0} -> {1}" -f $l[0], $f)
}
