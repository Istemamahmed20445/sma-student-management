#!/bin/bash

# Firebase Deployment Script for Student Management System
# This script deploys Firestore rules and Storage rules to Firebase

echo "🚀 Starting Firebase deployment..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI is not installed. Please install it first:"
    echo "npm install -g firebase-tools"
    exit 1
fi

# Check if user is logged in
if ! firebase projects:list &> /dev/null; then
    echo "❌ You are not logged in to Firebase. Please login first:"
    echo "firebase login"
    exit 1
fi

# Initialize Firebase if not already done
if [ ! -f "firebase.json" ]; then
    echo "📝 Initializing Firebase project..."
    firebase init --project sma-student
fi

# Deploy Firestore rules
echo "📊 Deploying Firestore rules..."
firebase deploy --only firestore:rules --project sma-student

if [ $? -eq 0 ]; then
    echo "✅ Firestore rules deployed successfully!"
else
    echo "❌ Failed to deploy Firestore rules"
    exit 1
fi

# Deploy Storage rules
echo "💾 Deploying Storage rules..."
firebase deploy --only storage --project sma-student

if [ $? -eq 0 ]; then
    echo "✅ Storage rules deployed successfully!"
else
    echo "❌ Failed to deploy Storage rules"
    exit 1
fi

# Deploy Firestore indexes (if any)
if [ -f "firestore.indexes.json" ]; then
    echo "🔍 Deploying Firestore indexes..."
    firebase deploy --only firestore:indexes --project sma-student
    
    if [ $? -eq 0 ]; then
        echo "✅ Firestore indexes deployed successfully!"
    else
        echo "❌ Failed to deploy Firestore indexes"
        exit 1
    fi
fi

echo "🎉 Firebase deployment completed successfully!"
echo ""
echo "📋 Summary:"
echo "   - Firestore rules: ✅ Deployed"
echo "   - Storage rules: ✅ Deployed"
echo "   - Project: sma-student"
echo ""
echo "🔗 Firebase Console: https://console.firebase.google.com/project/sma-student"
echo ""
echo "📚 Next steps:"
echo "   1. Test your rules in the Firebase Console"
echo "   2. Run 'python manage.py init_firebase' to initialize data"
echo "   3. Start your Django server: 'python manage.py runserver'"
