@echo off
setlocal

REM Point this repo to versioned hooks.
git config core.hooksPath .githooks
if errorlevel 1 (
  echo Failed to set core.hooksPath
  exit /b 1
)

REM Optional child setup, not committed to GitHub.
set "HOOK_CHILD=%~1"
if "%HOOK_CHILD%"=="" set "HOOK_CHILD=%PUBLISH_CHILD%"
if not "%HOOK_CHILD%"=="" (
  git config --local hooks.child "%HOOK_CHILD%"
  if errorlevel 1 (
    echo Failed to set hooks.child
    exit /b 1
  )
  echo Local hooks.child set to %HOOK_CHILD%
) else (
  echo No child provided. Set later with: git config --local hooks.child ^<name^>
)

echo Git hooks installed from .githooks
endlocal
