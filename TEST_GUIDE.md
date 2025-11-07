# Classroom Interaction Platform - Complete Testing Guide

## 📋 Table of Contents
1. [Test Environment Setup](#test-environment-setup)
2. [User Roles and Accounts](#user-roles-and-accounts)
3. [Feature Testing Checklist](#feature-testing-checklist)
4. [Detailed Test Cases](#detailed-test-cases)
5. [Known Issues and Expected Behavior](#known-issues-and-expected-behavior)

---

## 🔧 Test Environment Setup

### Prerequisites
- Python 3.8+
- MySQL database
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Start the Application
```bash
# Navigate to project directory
cd /Users/dududu/Documents/GitHub/groupproject-team_5

# Start the server
python3 run.py
```

### Access URL
- **Local URL**: http://localhost:5001
- **Default Admin Account**: 
  - Email: `admin@example.com`
  - Password: `admin123`

---

## 👥 User Roles and Accounts

### Default Test Accounts

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Admin | admin@example.com | admin123 | Full system access |
| Instructor | teacher@example.com | teacher123 | Course management |
| Student | student@example.com | student123 | Course participation |

---

## ✅ Feature Testing Checklist

### 🔐 Authentication System
- [ ] User registration
- [ ] User login
- [ ] User logout
- [ ] Role-based access control
- [ ] Session management

### 📚 Course Management
- [ ] Create new course (Admin/Instructor)
- [ ] View all courses list
- [ ] View course details
- [ ] Edit course information (Admin/Owner)
- [ ] Delete course (Admin/Owner)
- [ ] Course pagination (6 per page) - Admin/Instructor
- [ ] Student course pagination (6 per page) - My Courses
- [ ] Import students from CSV
- [ ] View enrolled students

### 🎯 Activity Management
- [ ] Create activity (Quiz/Poll/Word Cloud/Short Answer)
- [ ] View activity list
- [ ] View activity details
- [ ] View activity results
- [ ] Delete activity (Admin/Owner)
- [ ] Activity pagination (10 per page)
- [ ] Student participation in Quiz
- [ ] Student participation in Poll
- [ ] Student participation in Word Cloud
- [ ] Real-time response display

### 💬 Q&A System
- [ ] Ask question
- [ ] View question list
- [ ] View question details
- [ ] Submit answer
- [ ] Vote on answers (upvote)
- [ ] Mark best answer (Instructor only)
- [ ] Delete question (Admin/Instructor)
- [ ] Delete answer (Admin/Instructor/Author)
- [ ] Q&A pagination (10 per page)

### 📊 Dashboard Features
- [ ] Admin dashboard statistics
- [ ] Instructor dashboard overview
- [ ] Student dashboard courses
- [ ] Course analytics
- [ ] Activity statistics

---

## 🧪 Detailed Test Cases

## 1. Authentication Testing

### Test 1.1: User Login
**Steps:**
1. Navigate to http://localhost:5001
2. Click "Login" button
3. Enter credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
4. Click "Login"

**Expected Results:**
- ✅ Redirected to admin dashboard
- ✅ Welcome message displayed
- ✅ User menu shows admin options

### Test 1.2: Invalid Login
**Steps:**
1. Go to login page
2. Enter wrong credentials
3. Submit form

**Expected Results:**
- ❌ Error message: "Invalid email or password"
- ❌ Stays on login page

### Test 1.3: Logout
**Steps:**
1. Click user menu (top right)
2. Click "Logout"

**Expected Results:**
- ✅ Redirected to login page
- ✅ Message: "You have been logged out"

---

## 2. Course Management Testing

### Test 2.1: Create New Course (Admin/Instructor)
**Steps:**
1. Login as admin or instructor
2. Navigate to "Courses" → "Course List"
3. Click "Create Course" button
4. Fill in form:
   - **Course Name**: "Software Engineering 2024"
   - **Semester**: "Fall 2024"
   - **Description**: "Introduction to software engineering principles"
5. Click "Create Course"

**Expected Results:**
- ✅ Success message: "Course created successfully!"
- ✅ Redirected to course detail page
- ✅ New course appears in course list

### Test 2.2: View Course List with Pagination
**Steps:**
1. Navigate to "Courses" → "Course List"
2. Note the number of courses displayed
3. If more than 6 courses exist, check pagination controls
4. Click "Next" to view next page
5. Click page number to jump to specific page
6. Click "Previous" to go back

**Expected Results:**
- ✅ Maximum 6 courses per page
- ✅ Pagination controls visible when courses > 6
- ✅ Page numbers displayed correctly
- ✅ "Previous" disabled on first page
- ✅ "Next" disabled on last page
- ✅ Current page highlighted

### Test 2.3: View Course Details
**Steps:**
1. From course list, click on course name
2. Review course information displayed

**Expected Results:**
- ✅ Course name, semester, description shown
- ✅ Instructor information displayed
- ✅ Number of enrolled students visible
- ✅ Number of activities visible
- ✅ Activity list shown (if any exist)
- ✅ Q&A section accessible

### Test 2.4: Edit Course (Admin/Owner Only)
**Steps:**
1. Navigate to course list
2. Click pencil icon (✏️) on a course card
3. Modify course information:
   - Update name, semester, or description
4. Click "Save Changes"

**Expected Results:**
- ✅ Success message: "Course information updated successfully!"
- ✅ Changes reflected in course details
- ✅ Edit button only visible to admin/owner

### Test 2.5: Delete Course (Admin/Owner Only)
**Steps:**
1. Navigate to course list
2. Click trash icon (🗑️) on a course card
3. Confirm deletion in popup dialog

**Expected Results:**
- ✅ Confirmation dialog appears with warning message
- ✅ Upon confirmation, success message shown
- ✅ Course removed from list
- ✅ All related data deleted (enrollments, activities, Q&A)
- ✅ Delete button only visible to admin/owner

### Test 2.6: Import Students from CSV
**Steps:**
1. Login as admin or instructor
2. Navigate to course detail page
3. Click "Import Students" button
4. Upload CSV file with format:
   ```csv
   name,email,student_id
   John Doe,john@example.com,S001
   Jane Smith,jane@example.com,S002
   ```
5. Click "Import"

**Expected Results:**
- ✅ Success message with number of imported students
- ✅ Students appear in enrollment list
- ✅ Default passwords generated
- ✅ Duplicate emails handled gracefully

---

## 3. Activity Management Testing

### Test 3.1: Create Quiz Activity
**Steps:**
1. Login as instructor
2. Navigate to course detail page
3. Click "Create Activity"
4. Fill in form:
   - **Title**: "Midterm Quiz - Chapter 1"
   - **Type**: Select "Quiz"
   - **Question**: "What is software engineering?"
   - **Duration**: 30 (minutes)
5. Click "Create Activity"

**Expected Results:**
- ✅ Success message displayed
- ✅ Activity appears in activity list
- ✅ Activity marked as "Active"
- ✅ Duration countdown visible to students

### Test 3.2: Create Poll Activity
**Steps:**
1. Navigate to course and click "Create Activity"
2. Fill in form:
   - **Title**: "Course Feedback Poll"
   - **Type**: Select "Poll"
   - **Question**: "How would you rate this course?"
   - **Options**: Enter options separated by commas:
     ```
     Excellent, Good, Fair, Poor
     ```
   - **Duration**: 60
3. Submit form

**Expected Results:**
- ✅ Poll created successfully
- ✅ Options displayed correctly
- ✅ Students can select one option
- ✅ Results shown in real-time

### Test 3.3: Create Word Cloud Activity
**Steps:**
1. Navigate to course and click "Create Activity"
2. Fill in form:
   - **Title**: "Key Concepts - Chapter 3"
   - **Type**: Select "Word Cloud"
   - **Question**: "What is the first word that comes to mind when you think of this chapter?"
   - **Duration**: 15
3. Submit form

**Expected Results:**
- ✅ Word Cloud activity created successfully
- ✅ No options field required (unlike polls)
- ✅ Students can submit single words or short phrases
- ✅ Results display words in cloud format

### Test 3.4: Student Word Cloud Participation
**Steps:**
1. Login as student
2. Navigate to enrolled course
3. Click on active word cloud activity
4. Enter a word or short phrase (e.g., "Innovation", "Programming", "Algorithm")
5. Click "Submit"

**Expected Results:**
- ✅ Response submitted successfully
- ✅ Cannot submit twice
- ✅ Word appears in instructor's word cloud view
- ✅ Frequently submitted words appear larger

### Test 3.5: View Activity List with Pagination
**Steps:**
1. Navigate to "Activities" → "Activity List"
2. Observe activities displayed
3. If more than 10 activities exist:
   - Check pagination controls
   - Navigate between pages
   - Test page jumping

**Expected Results:**
- ✅ Maximum 10 activities per page
- ✅ Pagination works correctly
- ✅ Activity status (Active/Ended) shown
- ✅ Activity type (Quiz/Poll/Word Cloud) displayed

### Test 3.6: Student Participation
**Steps:**
1. Login as student
2. Navigate to enrolled course
3. Click on active activity
4. Submit response:
   - For Quiz: Type answer
   - For Poll: Select option
   - For Word Cloud: Enter a word
5. Click "Submit"

**Expected Results:**
- ✅ Response submitted successfully
- ✅ Cannot submit twice
- ✅ "Already submitted" message shown
- ✅ Can view own submission

### Test 3.7: View Activity Results (Instructor)
**Steps:**
1. Login as instructor
2. Navigate to activity list
3. Click "View Results" (📊) button on activity
4. Review analytics

**Expected Results:**
- ✅ Total submission count displayed
- ✅ For Quiz: All text answers shown
- ✅ For Poll: Bar chart with percentages
- ✅ For Word Cloud: Words displayed with frequency/size
- ✅ Student list with responses
- ✅ Export option available (if implemented)

### Test 3.8: Delete Activity

### Test 3.4: Student Participation
**Steps:**
1. Login as student
2. Navigate to enrolled course
3. Click on active activity
4. Submit response:
   - For Quiz: Type answer
   - For Poll: Select option
5. Click "Submit"

**Expected Results:**
- ✅ Response submitted successfully
- ✅ Cannot submit twice
- ✅ "Already submitted" message shown
- ✅ Can view own submission

### Test 3.5: View Activity Results (Instructor)
**Steps:**
1. Login as instructor
2. Navigate to activity list
3. Click "View Results" (📊) button on activity
4. Review analytics

**Expected Results:**
- ✅ Total submission count displayed
- ✅ For Quiz: All text answers shown
- ✅ For Poll: Bar chart with percentages
- ✅ Student list with responses
- ✅ Export option available (if implemented)

### Test 3.8: Delete Activity
**Steps:**
1. As instructor, go to activity list
2. Click trash icon (🗑️) on activity
3. Confirm deletion

**Expected Results:**
- ✅ Confirmation dialog with warning
- ✅ Activity deleted successfully
- ✅ All student responses deleted
- ✅ Statistics updated

### Test 3.9: Activity Cannot Be Edited (Verify)
**Steps:**
1. Navigate to activity list
2. Check for edit button

**Expected Results:**
- ✅ No edit button present (by design)
- ✅ Only view and delete options available
- ✅ This ensures data integrity

---

## 4. Q&A System Testing

### Test 4.1: Ask Question
**Steps:**
1. Login as student or instructor
2. Navigate to course Q&A section
3. Click "Ask Question"
4. Fill in form:
   - **Title**: "How to install Python?"
   - **Content**: "I'm having trouble installing Python on Windows. Can someone help?"
5. Click "Post Question"

**Expected Results:**
- ✅ Message: "Question published successfully!"
- ✅ Redirected to Q&A list
- ✅ Question appears at top of list
- ✅ View count starts at 0

### Test 4.2: View Question List with Pagination
**Steps:**
1. Navigate to course Q&A section
2. Observe questions displayed (10 per page)
3. Test pagination if applicable

**Expected Results:**
- ✅ 10 questions per page
- ✅ Sorted by newest first
- ✅ Shows question title, author, timestamp
- ✅ Shows answer count
- ✅ Shows "Resolved" badge if best answer marked

### Test 4.3: View Question Details
**Steps:**
1. Click on question title
2. Review question page

**Expected Results:**
- ✅ Full question content shown
- ✅ View count incremented
- ✅ All answers displayed
- ✅ Best answer (if any) shown at top
- ✅ Answer form available at bottom

### Test 4.4: Submit Answer
**Steps:**
1. Scroll to answer form
2. Enter answer content:
   ```
   You can download Python from python.org. 
   Make sure to check "Add Python to PATH" during installation.
   ```
3. Click "Submit Answer"

**Expected Results:**
- ✅ Message: "Answer submitted successfully!"
- ✅ Answer appears in list
- ✅ Answer count updated
- ✅ Instructor answers marked with special badge

### Test 4.5: Vote on Answer
**Steps:**
1. Find an answer in question detail page
2. Click upvote button (👍)
3. Click again to remove vote

**Expected Results:**
- ✅ Vote count increases
- ✅ Button color changes when voted
- ✅ Click again removes vote
- ✅ Vote count decreases
- ✅ Message: "Vote successful"

### Test 4.6: Mark Best Answer (Instructor Only)
**Steps:**
1. Login as course instructor
2. Navigate to question with answers
3. Click "Mark as Best Answer" on preferred answer

**Expected Results:**
- ✅ Success message: "Marked as best answer"
- ✅ Best answer moved to top
- ✅ Special badge/highlight applied
- ✅ Question marked as "Resolved"
- ✅ Only one best answer allowed

### Test 4.7: Delete Question (Admin/Instructor)
**Steps:**
1. Login as admin or course instructor
2. Go to question list
3. Click delete button (🗑️) on question
4. Confirm deletion

**Expected Results:**
- ✅ Confirmation dialog appears
- ✅ Message: "Question deleted successfully"
- ✅ All answers deleted
- ✅ All votes deleted
- ✅ Question removed from list

### Test 4.8: Delete Answer (Admin/Instructor/Author)
**Steps:**
1. Navigate to question detail
2. Click delete on an answer
3. Confirm

**Expected Results:**
- ✅ Answer deleted successfully
- ✅ Vote records deleted
- ✅ If it was best answer, "Resolved" status removed
- ✅ Answer count updated

---

## 5. Dashboard Testing

### Test 5.1: Admin Dashboard
**Steps:**
1. Login as admin
2. Navigate to dashboard

**Expected Results:**
- ✅ Total courses count displayed
- ✅ Total users count shown
- ✅ Total activities count visible
- ✅ Recent activities listed
- ✅ System statistics charts (if implemented)

### Test 5.2: Instructor Dashboard
**Steps:**
1. Login as instructor
2. View dashboard

**Expected Results:**
- ✅ "My Courses" count shown
- ✅ "Active Activities" count displayed
- ✅ Course list with quick links
- ✅ Recent activities preview
- ✅ "Create Course" button visible

### Test 5.3: Student Dashboard
**Steps:**
1. Login as student
2. View dashboard

**Expected Results:**
- ✅ Enrolled courses displayed
- ✅ Active activities in enrolled courses shown
- ✅ Quick access to Q&A
- ✅ "Browse Courses" option available

---

## 6. Pagination Testing (Critical)

### Test 6.1: Course List Pagination (Admin & Instructor)
**Preparation:**
- Ensure database has at least 15 courses

**Steps:**
1. Login as admin or instructor
2. Navigate to course list
3. Verify only 6 courses on page 1
4. Click "Next" → verify page 2 shows 6 courses
5. Click "Next" → verify page 3 shows remaining courses
6. Click page number "1" → verify returns to first page
7. Test "Previous" button functionality

**Expected Results:**
- ✅ Exactly 6 courses per page
- ✅ Navigation buttons work correctly
- ✅ Page indicators accurate
- ✅ URL updates with page parameter
- ✅ Total count displayed: "Showing page X of Y (Z courses total)"

### Test 6.2: Student Course Pagination (My Courses)
**Preparation:**
- Student should be enrolled in at least 10 courses

**Steps:**
1. Login as student (e.g., student1@example.com)
2. Navigate to "My Courses"
3. Verify only 6 courses on page 1
4. Click "Next" → verify page 2 shows next 6 courses
5. Test pagination controls
6. Verify all enrolled courses appear

**Expected Results:**
- ✅ Exactly 6 courses per page
- ✅ Pagination controls work for student view
- ✅ Only shows enrolled courses
- ✅ Navigation smooth and accurate

### Test 6.3: Activity List Pagination
**Preparation:**
- Create at least 25 activities in a course

**Steps:**
1. Navigate to activity list
2. Count activities on page 1 (should be 10)
3. Navigate through all pages
4. Test all pagination controls

**Expected Results:**
- ✅ 10 activities per page
- ✅ Correct page count calculation
- ✅ Smooth navigation between pages

### Test 6.4: Q&A List Pagination
**Preparation:**
- Create at least 30 questions in a course

**Steps:**
1. Go to course Q&A section
2. Verify 10 questions on first page
3. Test pagination controls
4. Jump to last page
5. Return to first page

**Expected Results:**
- ✅ 10 questions per page
- ✅ Pagination info accurate
- ✅ No duplicate questions across pages

---

## 7. Permission and Access Control Testing

### Test 7.1: Student Access Restrictions
**Steps:**
1. Login as student
2. Try to access:
   - Course creation page
   - Other students' courses
   - Admin dashboard
   - Edit course page

**Expected Results:**
- ❌ "Create Course" button not visible
- ❌ Cannot access non-enrolled courses
- ❌ Redirected with permission error
- ✅ Can only view enrolled courses

### Test 7.2: Instructor Permissions
**Steps:**
1. Login as instructor
2. Verify can:
   - Create courses
   - Edit own courses
   - Delete own courses
   - Create activities in own courses
   - Delete activities in own courses
   - Delete questions in own courses
3. Verify cannot:
   - Edit other instructors' courses
   - Delete other instructors' courses
   - Access admin dashboard

**Expected Results:**
- ✅ Full control over own courses
- ❌ No access to others' courses
- ✅ Appropriate error messages

### Test 7.3: Admin Full Access
**Steps:**
1. Login as admin
2. Verify can:
   - View all courses
   - Edit any course
   - Delete any course
   - Delete any question
   - Delete any activity
   - View all statistics

**Expected Results:**
- ✅ Full system access
- ✅ All management buttons visible
- ✅ Can perform all operations

---

## 8. Data Integrity Testing

### Test 8.1: Cascade Delete - Course
**Steps:**
1. Create a course with:
   - 5 enrolled students
   - 3 activities with student responses
   - 10 Q&A questions with answers
2. Delete the course
3. Verify all related data deleted

**Expected Results:**
- ✅ All enrollments deleted
- ✅ All activities deleted
- ✅ All responses deleted
- ✅ All questions deleted
- ✅ All answers deleted
- ✅ All votes deleted
- ✅ No orphaned data in database

### Test 8.2: Cascade Delete - Question
**Steps:**
1. Create question with:
   - 5 answers
   - 10 votes on answers
   - One marked as best answer
2. Delete question
3. Check database

**Expected Results:**
- ✅ All answers deleted
- ✅ All votes deleted
- ✅ No foreign key errors
- ✅ Clean deletion

### Test 8.3: Best Answer Constraint
**Steps:**
1. Create question with 3 answers
2. Mark answer 1 as best
3. Try to delete answer 1

**Expected Results:**
- ✅ Best answer mark removed first
- ✅ Answer deleted successfully
- ✅ Question marked as unresolved
- ✅ No foreign key errors

---

## 9. UI/UX Testing

### Test 9.1: Responsive Design
**Steps:**
1. Test on different screen sizes:
   - Desktop (1920x1080)
   - Laptop (1366x768)
   - Tablet (768x1024)
   - Mobile (375x667)

**Expected Results:**
- ✅ Layout adjusts appropriately
- ✅ Navigation menu responsive
- ✅ Cards stack on mobile
- ✅ No horizontal scrolling
- ✅ Buttons accessible

### Test 9.2: Flash Messages
**Steps:**
1. Perform various actions
2. Observe flash messages

**Expected Results:**
- ✅ Success messages in green
- ✅ Error messages in red
- ✅ Messages auto-dismiss after 5 seconds
- ✅ Messages dismissible manually
- ✅ All messages in English

### Test 9.3: Loading States
**Steps:**
1. Submit forms
2. Delete items
3. Navigate between pages

**Expected Results:**
- ✅ Loading indicators shown
- ✅ Buttons disabled during processing
- ✅ No double submissions possible

---

## 10. Edge Cases and Error Handling

### Test 10.1: Empty States
**Steps:**
1. View course list with no courses
2. View activity list with no activities
3. View Q&A with no questions

**Expected Results:**
- ✅ Friendly "no data" message shown
- ✅ Call-to-action buttons displayed
- ✅ No error messages

### Test 10.2: Invalid Input
**Steps:**
1. Try to create course with empty name
2. Submit empty question
3. Submit empty answer

**Expected Results:**
- ❌ Validation error shown
- ❌ Form not submitted
- ✅ Error message in English
- ✅ User remains on form page

### Test 10.3: Concurrent Operations
**Steps:**
1. Open same course in two browsers
2. Delete course in browser 1
3. Try to access it in browser 2

**Expected Results:**
- ✅ 404 error shown
- ✅ Graceful error handling
- ✅ Appropriate error message

---

## 📊 Test Results Template

Use this template to track your testing:

```
Test Date: _______________
Tester: _______________
Browser: _______________
Test Environment: _______________

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | User Login | ✅ PASS |  |
| 1.2 | Invalid Login | ✅ PASS |  |
| 2.1 | Create Course | ✅ PASS |  |
| 2.2 | Course Pagination | ⚠️ ISSUE | Needs 15+ courses |
| ... | ... | ... | ... |

Issues Found:
1. 
2. 
3. 

Recommendations:
1.
2.
3.
```

---

## 🐛 Known Issues and Expected Behavior

### Expected Behaviors (Not Bugs)
1. **Activity Edit Disabled**: Activities cannot be edited after creation to maintain data integrity
2. **Delete Confirmations**: All delete operations show confirmation dialogs
3. **Pagination Limits**: Fixed items per page (courses: 6, activities: 10, Q&A: 10)
4. **Access Restrictions**: Students can only see enrolled courses
5. **Best Answer Unique**: Only one answer can be marked as best per question

### Common Testing Pitfalls
1. **Insufficient Data**: Some tests require minimum data volumes (15+ courses for pagination)
2. **Permission Errors**: Testing with wrong user role will show expected permission errors
3. **Cache Issues**: Clear browser cache if updates don't appear
4. **Session Timeout**: Long idle periods may require re-login

---

## 📝 Test Completion Checklist

### Before Submitting Test Report:
- [ ] All authentication tests passed
- [ ] All CRUD operations tested for courses
- [ ] All CRUD operations tested for activities
- [ ] All CRUD operations tested for Q&A
- [ ] Pagination tested with sufficient data
- [ ] Permissions tested for all roles
- [ ] Delete operations with cascade verified
- [ ] All flash messages in English
- [ ] UI responsive on multiple devices
- [ ] No console errors in browser developer tools
- [ ] All edge cases handled gracefully

---

## 🚀 Quick Test Script

For rapid testing, run these commands in sequence:

```bash
# 1. Start server
python3 run.py

# 2. Open multiple browser tabs:
# Tab 1: Login as admin (admin@example.com / admin123)
# Tab 2: Login as instructor (teacher@example.com / teacher123)
# Tab 3: Login as student (student@example.com / student123)

# 3. Test in order:
# - Create 15 courses (admin)
# - Create 25 activities in one course (instructor)
# - Create 30 questions in one course (student)
# - Test all pagination
# - Test all delete operations
# - Verify cascade deletes
```

---

## 📞 Support

If you encounter issues during testing:
1. Check browser console for errors (F12)
2. Check terminal for server errors
3. Verify database connection
4. Ensure all dependencies installed
5. Review this guide for expected behavior

---

**Last Updated**: 2025-01-07
**Version**: 1.0
**Tested On**: macOS, Python 3.10+, MySQL 8.0+
