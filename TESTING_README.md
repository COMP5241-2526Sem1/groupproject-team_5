# Testing Documentation

This directory contains comprehensive testing documentation and tools for the Classroom Interaction Platform.

## 📚 Files

1. **TEST_GUIDE.md** - Complete testing manual with detailed test cases
2. **generate_test_data.py** - Script to automatically generate test data
3. **This README** - Quick start guide

## 🚀 Quick Start

### Step 1: Generate Test Data

Run the test data generator to create sample courses, users, activities, and Q&A content:

```bash
# From project root directory
python3 generate_test_data.py
```

This will create:
- 1 Admin account
- 5 Instructor accounts
- 30 Student accounts
- 20 Courses
- 30+ Activities
- 40+ Q&A Questions with answers
- Enrollments and responses

**Default Test Accounts:**
- **Admin**: admin@example.com / admin123
- **Instructors**: instructor1@example.com to instructor5@example.com / password123
- **Students**: student1@example.com to student30@example.com / password123

### Step 2: Start the Application

```bash
python3 run.py
```

Access at: http://localhost:5001

### Step 3: Follow Test Guide

Open `TEST_GUIDE.md` and follow the detailed test cases:
- Authentication testing
- Course management (with pagination)
- Activity management (with pagination)
- Q&A system (with pagination)
- Permission testing
- Data integrity testing

## 🧪 Testing Pagination

The test data generator creates enough data to test pagination:
- **Courses**: 20 courses (6 per page = 4 pages)
- **Activities**: 30+ activities (10 per page = 3+ pages)
- **Q&A**: 40+ questions (10 per page = 4+ pages)

## ✅ Testing Checklist

### Core Features
- [ ] User authentication (login/logout)
- [ ] Course CRUD operations
- [ ] Course pagination (6 per page)
- [ ] Activity creation and deletion
- [ ] Activity pagination (10 per page)
- [ ] Student participation in activities
- [ ] Q&A question posting
- [ ] Q&A answer submission
- [ ] Q&A pagination (10 per page)
- [ ] Answer voting
- [ ] Best answer marking

### Permissions
- [ ] Admin full access
- [ ] Instructor course management
- [ ] Student enrollment restrictions
- [ ] Delete permissions

### Data Integrity
- [ ] Cascade delete for courses
- [ ] Cascade delete for questions
- [ ] Foreign key constraint handling

## 🎯 Priority Test Cases

### High Priority
1. **Course Pagination** - Ensure 6 courses per page
2. **Activity Pagination** - Ensure 10 activities per page
3. **Q&A Pagination** - Ensure 10 questions per page
4. **Delete Operations** - Test all cascade deletes
5. **Permissions** - Verify role-based access

### Medium Priority
1. Student participation in activities
2. Q&A voting system
3. Best answer functionality
4. Flash message display

### Low Priority
1. UI responsiveness
2. Loading states
3. Empty state displays

## 📊 Test Report Template

After testing, document results:

```
Test Date: _______________
Tester: _______________
Browser: _______________

Summary:
- Total Tests: ___
- Passed: ___
- Failed: ___
- Blocked: ___

Critical Issues:
1. 
2. 

Minor Issues:
1.
2.

Recommendations:
1.
2.
```

## 🐛 Common Issues

### Data Generation Fails
- **Solution**: Check database connection
- **Solution**: Ensure migrations are up to date

### Pagination Not Working
- **Solution**: Ensure enough data exists (run generator again)
- **Solution**: Clear browser cache

### Permission Errors
- **Solution**: Verify you're logged in with correct role
- **Solution**: Check test account credentials

## 📝 Additional Testing

### Manual Testing
- Test with different browsers (Chrome, Firefox, Safari)
- Test on different devices (desktop, tablet, mobile)
- Test with slow internet connection

### Performance Testing
- Load test with many concurrent users
- Check database query performance
- Monitor memory usage

### Security Testing
- Verify password hashing
- Test SQL injection prevention
- Check XSS protection

## 🔄 Reset Test Data

To reset and regenerate test data:

```bash
# Option 1: Delete database and regenerate
rm instance/classroom.db
python3 run.py  # Initialize fresh database
python3 generate_test_data.py

# Option 2: Just add more data
python3 generate_test_data.py  # Adds more data
```

## 📖 Documentation

For detailed test procedures, see:
- **TEST_GUIDE.md** - Complete testing manual with step-by-step instructions
- **PROJECT_STRUCTURE.md** - System architecture overview
- **USER_MANUAL.md** - User guide for the platform

## 💡 Tips

1. **Use Different Browsers**: Test in Chrome, Firefox, and Safari
2. **Test Pagination Early**: Verify pagination works before detailed testing
3. **Keep Track**: Use the test results template to document findings
4. **Test Permissions**: Always test with different user roles
5. **Test Deletes Last**: Deletion tests remove data, so do them last

## 🎓 Learning Resources

While testing, you'll learn about:
- Flask web framework
- SQLAlchemy ORM
- Bootstrap UI framework
- Role-based access control
- Database relationships and constraints
- Pagination implementation

## 🤝 Contributing

Found a bug during testing? 
1. Document it clearly
2. Include steps to reproduce
3. Note expected vs actual behavior
4. Include screenshots if applicable

---

**Happy Testing! 🚀**

For questions or issues, refer to TEST_GUIDE.md for detailed instructions.
