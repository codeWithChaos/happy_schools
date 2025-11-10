# Phase 8: Communications Module - Testing Guide

## Overview

Phase 8 Communications Module has been successfully implemented with complete backend views, URL routing, and frontend templates for announcements, messages, and notifications.

## Features Implemented

### 1. Announcements System

- **Create/Edit Announcements**: Admin and teachers can create announcements
- **Target Audience**: All Users, Students Only, Parents Only, Teachers Only, Staff Only, Specific Classes
- **Priority Levels**: Low, Normal, High, Urgent
- **Publishing Controls**: Draft/Published status, publish date, expiry date
- **Pinning**: Pin important announcements to top
- **Attachments**: Support for file attachments
- **Filters**: Status, priority, target audience, search

### 2. Direct Messaging

- **Inbox/Sent**: Separate views for received and sent messages
- **Compose**: Send messages to any user in the same school
- **Reply**: Reply to messages with threading support
- **Star**: Star important messages
- **Attachments**: Support for file attachments
- **Soft Delete**: Messages deleted from sender/recipient view separately
- **Read Status**: Automatic read tracking

### 3. Notifications System

- **Types**: Announcement, Message, Attendance, Fee, Exam, Result, Timetable, System
- **Auto-creation**: Notifications created automatically (e.g., when receiving messages)
- **Mark as Read**: Individual and bulk mark as read
- **Filters**: Status (read/unread), type
- **Action Links**: Notifications can link to relevant pages

## Files Created/Modified

### Views (apps/communications/views.py)

**Announcements (5 views):**
- AnnouncementListView - List with filters (status, priority, target, search)
- AnnouncementCreateView - Create with role-based access (admin/teacher)
- AnnouncementUpdateView - Edit announcements
- AnnouncementDeleteView - Delete with confirmation
- AnnouncementDetailView - View announcement details

**Messages (7 views):**
- MessageInboxView - View received messages with filters
- MessageSentView - View sent messages
- MessageComposeView - Compose new message or reply
- MessageDetailView - View message details (auto mark as read)
- MessageDeleteView - Soft delete messages
- MessageToggleStarView - Star/unstar messages

**Notifications (4 views):**
- NotificationListView - List with filters (status, type)
- NotificationMarkReadView - Mark single notification as read
- NotificationMarkAllReadView - Bulk mark all as read
- NotificationDeleteView - Delete notification

### URLs (apps/communications/urls.py)

- **5 routes** for announcements (list, create, detail, edit, delete)
- **6 routes** for messages (inbox, sent, compose, detail, delete, star)
- **4 routes** for notifications (list, mark read, mark all read, delete)
- **Total: 15 URL patterns**

### Templates

**Announcements (4 templates):**
1. `list.html` - Announcements list with filters and badges
2. `form.html` - Create/Edit form with all fields
3. `confirm_delete.html` - Delete confirmation
4. `detail.html` - Full announcement view with metadata

**Messages (4 templates):**
1. `inbox.html` - Inbox with unread count and filters
2. `sent.html` - Sent messages list
3. `compose.html` - Message composition form
4. `detail.html` - Message view with reply and star options

**Notifications (1 template):**
1. `list.html` - Notifications list with icons and filters

## Testing Steps

### Test 1: Create and Manage Announcements

1. **Login as admin/teacher**
2. **Navigate to Communications → Announcements**
3. **Create announcement:**
   - Click "Create Announcement"
   - Fill in title: "Important Notice"
   - Add content
   - Set priority: "High"
   - Select target audience: "All Users"
   - Check "Publish Now"
   - Check "Pin Announcement"
   - Click "Create Announcement"
4. **Verify:**
   - Announcement appears at top of list (pinned)
   - High priority badge shown
   - Published status displayed

5. **Filter announcements:**
   - Test status filter (Published/Draft/Expired)
   - Test priority filter
   - Test search functionality

6. **Edit announcement:**
   - Click "Edit" on an announcement
   - Change priority to "Urgent"
   - Update content
   - Save
   - Verify changes reflected

7. **View details:**
   - Click on announcement title
   - Verify all details shown correctly
   - Check attachment download (if uploaded)

8. **Delete announcement:**
   - Click "Delete"
   - Confirm deletion
   - Verify removed from list

### Test 2: Direct Messaging

1. **Access inbox:**
   - Navigate to Communications → Messages → Inbox
   - Should see unread count if any unread messages

2. **Compose new message:**
   - Click "Compose"
   - Select recipient from dropdown
   - Enter subject: "Test Message"
   - Enter content
   - Optionally upload attachment
   - Click "Send Message"
   - **Verify:** Redirected to sent messages, success message shown

3. **Check sent messages:**
   - Navigate to "Sent" tab
   - Find sent message
   - Status should show "Sent" or "Read"

4. **Receive and read message:**
   - **Login as recipient user**
   - Navigate to Inbox
   - Should see new message (unread, blue background)
   - Click on message to view
   - **Verify:** Message automatically marked as read

5. **Reply to message:**
   - While viewing message, click "Reply"
   - Subject pre-filled with "Re: ..."
   - Enter reply content
   - Send
   - **Verify:** Reply sent, parent message info shown

6. **Star message:**
   - Click star icon on message
   - **Verify:** Star filled (yellow color)
   - Filter by "Starred" to see only starred messages

7. **Delete message:**
   - Click "Delete" button
   - **Verify:** Message removed from inbox
   - Original sender still sees message in sent folder (soft delete)

8. **Search messages:**
   - Use search box to find messages by subject/content/sender name

### Test 3: Notifications

1. **Trigger notification:**
   - Send a message to another user (creates notification automatically)
   - **Or** have system create notification via admin action

2. **View notifications:**
   - Click on user profile → Notifications (or direct link)
   - Should see unread count badge
   - Unread notifications have blue background

3. **Filter notifications:**
   - Test "Status" filter: All/Unread/Read
   - Test "Type" filter: Select different types

4. **Mark as read:**
   - Click "Mark Read" on single notification
   - **Verify:** Blue background removed, read status updated

5. **Mark all as read:**
   - With multiple unread notifications
   - Click "Mark All Read" button
   - **Verify:** All notifications marked as read, unread count becomes 0

6. **Delete notification:**
   - Click "Delete" on a notification
   - **Verify:** Notification removed from list

7. **Action links:**
   - For message notifications, verify clicking notification redirects to message
   - For other types, verify appropriate redirection

### Test 4: Role-Based Access

1. **Admin/Teacher access:**
   - Can create/edit/delete announcements ✓
   - Can send messages to any school user ✓
   - Can view all communications ✓

2. **Other roles (student/parent/staff):**
   - Can view published announcements ✓
   - Can send/receive messages ✓
   - Can view their notifications ✓
   - **Cannot** create announcements ✗

3. **Multi-tenancy:**
   - Users can only message users from same school ✓
   - Announcements filtered by school ✓
   - Notifications only for recipient user ✓

## Key Features to Verify

### Announcement Features

- **Pinning**: Pinned announcements show at top with pin icon
- **Priority badges**: Urgent (red), High (orange), Normal (blue), Low (gray)
- **Status badges**: Published (green), Draft (gray)
- **Target audience badge**: Shows who can see announcement
- **Expiry**: Announcements expire after expiry date
- **Attachments**: Can download attached files

### Message Features

- **Unread indicator**: Blue background for unread messages
- **Star functionality**: Toggle star on/off
- **Threading**: Reply chains show parent message
- **Soft delete**: Sender and recipient delete independently
- **Read receipts**: Shows "Read" or "Sent" status
- **Attachments**: Can send and download files

### Notification Features

- **Type icons**: Different icons for different notification types
- **Unread count**: Badge shows number of unread notifications
- **Timestamp**: Shows relative time (e.g., "5 minutes ago")
- **Bulk actions**: Mark all as read at once
- **Action links**: Click notification to go to relevant page

## Common Test Scenarios

### Scenario 1: Emergency Announcement

1. Admin creates urgent announcement
2. Sets priority to "Urgent"
3. Target: "All Users"
4. Pins announcement
5. Publishes immediately
6. **Expected**: All users see red "Urgent" badge, announcement at top

### Scenario 2: Class-Specific Announcement

1. Teacher creates announcement
2. Target: "Specific Class"
3. Selects multiple classes (e.g., Class 10 A, 10 B)
4. Publishes
5. **Expected**: Only students/parents of selected classes see it

### Scenario 3: Message Conversation

1. User A sends message to User B
2. User B receives notification
3. User B reads message and replies
4. User A receives reply notification
5. User A reads reply
6. **Expected**: Both see conversation thread, read status updates

### Scenario 4: Notification Workflow

1. Action triggers notification (e.g., new message)
2. Recipient sees notification with unread count
3. Recipient clicks notification
4. Redirected to relevant page (e.g., message detail)
5. Notification automatically marked as read
6. **Expected**: Seamless workflow, unread count decreases

## Business Logic Verification

### Announcement Publishing

```python
# Draft announcements
is_published = False → Not visible to regular users

# Published announcements
is_published = True → Visible based on target audience

# Scheduled publishing
publish_date > now → Not yet visible
publish_date <= now → Visible

# Expired announcements
expiry_date < now → Not visible (expired)
```

### Message Status

```python
# On send
status = 'sent', is_read = False

# On recipient view
status = 'read', is_read = True, read_at = now

# Soft delete
is_deleted_by_sender = True  # Sender deletes
is_deleted_by_recipient = True  # Recipient deletes
```

### Notification Creation

- **Automatic**: Created when certain actions occur (e.g., new message)
- **Manual**: Can be created programmatically for system events
- **Targeting**: Always for specific recipient user

## Troubleshooting

### Issue: Cannot create announcement

- **Solution**: Check if user role is admin or teacher
- **Solution**: Verify all required fields filled

### Issue: Messages not showing in inbox

- **Solution**: Check if message deleted by recipient (is_deleted_by_recipient)
- **Solution**: Verify multi-tenancy (same school)

### Issue: Notifications not appearing

- **Solution**: Check notification creation logic in views
- **Solution**: Verify recipient is correct user

### Issue: Attachments not downloading

- **Solution**: Check MEDIA_URL and MEDIA_ROOT configured
- **Solution**: Verify file uploaded correctly

## Next Steps

After testing Phase 8, proceed to:

- **Phase 9**: Dashboard Implementation (analytics, charts, quick stats from all modules)
- **Phase 10**: Testing & Documentation (unit tests, user docs, deployment guide)

## Technical Notes

- All views include multi-tenancy filtering
- Role-based access implemented via UserPassesTestMixin
- Soft delete for messages (separate flags for sender/recipient)
- Automatic read tracking for messages and notifications
- File upload support for announcements and messages
- Pagination: 20 items per page (announcements, messages), 30 (notifications)
- Search functionality for announcements and messages
- Filter options for all list views
