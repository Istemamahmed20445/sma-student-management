# SMA Logo Implementation Instructions

## 📁 **Where to Place Your Logo:**

1. **Save your JPEG logo** as: `static/images/sma-logo.jpg`
2. **Make sure the filename is exactly**: `sma-logo.jpg` (lowercase)

## 🎯 **What I've Updated:**

### ✅ **Header/Navigation Area** (`templates/base.html`)
- Replaced the graduation cap icon with your SMA logo
- Logo size: `h-8` (32px height) with auto width
- Fallback: Shows graduation cap if logo fails to load

### ✅ **Main Content Area** (`templates/core/home.html`)
- Replaced the large graduation cap icon with your SMA logo
- Logo size: `h-32` (128px height) with auto width
- Fallback: Shows graduation cap if logo fails to load

## 🔧 **Technical Details:**

- **Responsive Design**: Logos scale automatically on different screen sizes
- **Error Handling**: If logo file is missing, falls back to graduation cap icons
- **Static Files**: Uses Django's static file system for proper serving
- **Alt Text**: Includes proper accessibility attributes

## 📋 **Steps to Complete:**

1. **Save your JPEG logo** as `static/images/sma-logo.jpg`
2. **Test the website** - your logo should appear in both locations
3. **If logo doesn't show**: Check that the filename is exactly `sma-logo.jpg`

## 🎨 **Logo Specifications:**

- **Format**: JPEG
- **Filename**: `sma-logo.jpg` (exact case)
- **Location**: `static/images/` directory
- **Recommended Size**: 
  - Header: ~32px height (any width)
  - Homepage: ~128px height (any width)

## 🚀 **Ready to Test:**

Once you save your logo as `static/images/sma-logo.jpg`, refresh your browser and you should see your beautiful SMA logo with the caduceus symbol in both marked locations!

---

**Note**: The logo will automatically scale to fit the design while maintaining its aspect ratio.
