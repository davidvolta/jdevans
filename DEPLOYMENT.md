# Deployment Guide

This document explains how to manage deployments while preserving user-generated poems.

## Build Scripts

### For Local Development
```bash
./local-build.sh
```
- Resets poems to original state (removes test poems)
- Builds frontend and deploys to backend/static
- Safe to use during development

### For Production Deployment
```bash
./production-build.sh
```
- **Preserves user-generated poems** 
- Builds frontend and deploys to backend/static
- Does NOT reset poems.json
- Use this when deploying to production

## Backup & Restore (Extra Safety)

### Before Production Deployment (Optional)
```bash
./backup-user-data.sh
```
- Creates timestamped backup of user poems and images
- Stored in `backend/backups/YYYYMMDD_HHMMSS/`

### To Restore User Data
```bash
./restore-user-data.sh backend/backups/20231225_143022
```
- Restores poems and images from specific backup

## Deployment Workflow

### Current Situation
Your current `render-build.sh` resets poems, which deletes all user data.

### Recommended Process

**For Production:**
1. (Optional) Backup user data: `./backup-user-data.sh`
2. Build with: `./production-build.sh` 
3. Deploy to production
4. User poems remain intact ✅

**For Local Development:**
1. Use: `./local-build.sh`
2. This resets test poems for clean development environment

## File Locations

- **User Poems**: `backend/poems.json`
- **User Images**: `backend/static/images/`
- **Backups**: `backend/backups/`
- **Original Poems**: `backend/ORIGINAL_poems.json` (never changes)

## Migration Steps

1. Replace your current deployment process with `./production-build.sh`
2. Update any CI/CD scripts to use the new build script
3. Consider setting `ENV=production` environment variable in production