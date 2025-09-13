# Helpdesk Feature Development Guide

## Overview
This document outlines the implementation plan for enhancing the helpdesk frontend with new assignment rule features, holiday integration, and improved UI/UX consistency.

## Core Principles
- Maintain UI/UX consistency by reusing existing components
- Follow the existing folder structure and code patterns
- Fetch data from backend APIs following established patterns
- Ensure seamless integration with existing Settings UI (SLA policies, Assignment Rules)

## Recent Changes (2025-09-12)

### 1. Holiday Integration
- **File Modified:** `/helpdesk/api/holidays.py`
  - Now fetches from custom Holidays doctype (primary source)
  - Falls back to ERPNext Holiday List if Holidays doctype doesn't exist
  - Groups holidays by year for better display
  - Maintains backward compatibility with HD Holiday List

### 2. Assignment Rules API Enhancements
- **File Modified:** `/helpdesk/api/assignment_rule.py`
  - Added `get_assignment_rule_details()` for fetching rule with all fields
  - Added `save_assignment_rule()` for saving rules with custom fields
  - Added `get_work_schedules()` for predefined work schedules
  - Supports Dynamic User Assignments and Holiday Lists
  - Handles assignment days (Monday-Sunday) configuration

### 3. SLA Conditions with Employee Context
- **File Created:** `/helpdesk/api/sla_conditions.py`
  - `get_employee_fields()` - Returns employee fields for SLA conditions
  - `get_ticket_fields_for_conditions()` - Returns all available fields
  - `evaluate_sla_condition()` - Evaluates conditions with employee context
  - `get_condition_builder_options()` - Provides UI options for condition builder

- **File Modified:** `/helpdesk/utils.py`
  - Enhanced `get_context()` to include employee data
  - Fetches employee details when ticket has assigned user
  - Provides employee context for SLA condition evaluation

### 4. Category and Subcategory Filtering
- **File Created:** `/helpdesk/api/category.py`
  - `get_categories()` - Returns categories with their subcategories
  - `get_subcategories()` - Returns subcategories for a parent
  - `get_category_hierarchy()` - Returns complete hierarchy tree

- **File Created:** `/helpdesk/public/js/hd_ticket_category.js`
  - Client-side script for HD Ticket form
  - Filters categories to show only parent categories
  - Filters subcategories based on selected category
  - Enables/disables subcategory field dynamically

- **File Modified:** `/helpdesk/hooks.py`
  - Added `doctype_js` hook for HD Ticket category script

### 5. Database Structure
- Custom fields in HD Ticket:
  - `custom_category` (Link to HD Category)
  - `custom_sub_category` (Link to HD Category)
- HD Category doctype structure:
  - `is_sub_category` - Boolean to identify subcategories
  - `parent_category` - Link to parent category
  - `is_active` - Boolean for active status

## Implementation Status

✅ **Completed Components:**
- Dynamic User Assignment Selector Vue component
- Holiday Selector Vue component  
- Category/Subcategory Selector with parent filtering
- Assignment Rules store updates with new fields
- Backend API endpoints for all features
- Holiday API integration with custom Holidays doctype
- SLA conditions with employee field support
- Assignment Rules backend API enhancements

## Feature Requirements

### 1. Dynamic User Assignment Integration ✅

#### Background
- Integrate Dynamic User Assignment doctype from `apps/nextai/nextai/nextai/doctype/dynamic_user_assignment/`
- This doctype filters employees based on configurable conditions
- When linked with `pw_helpdesk`, it automatically sets users in teams

#### Implementation Tasks
- [ ] Add Dynamic User Assignment field to Assignment Rules
- [ ] Create UI component for selecting multiple Dynamic User Assignments
- [ ] Implement backend API integration for fetching Dynamic User Assignments
- [ ] Add validation for user assignment conditions
- [ ] Update team assignment logic to respect Dynamic User Assignment rules

#### Files to Modify
- `/desk/src/components/Settings/Assignment Rules/AssigneeRules.vue`
- `/desk/src/components/Settings/Assignment Rules/AssigneeSearch.vue`
- `/desk/src/stores/assignmentRules.ts`
- Backend: Assignment Rule doctype to add link table field

### 2. Holiday Integration for SLA ✅

#### Background
- Replace HD Holiday List with custom Holidays doctype
- Holidays doctype location: `apps/cn_leave_shift_managment/cn_leave_shift_managment/cn_leave_shift_managment/doctype/holidays/`
- Agent-specific holidays should affect SLA timing calculations
- SLA should carry forward based on agent's holiday schedule

#### Implementation Completed
- ✅ Updated `/helpdesk/api/holidays.py` to fetch from Holidays doctype
- ✅ Added fallback to ERPNext Holiday List if available
- ✅ Grouped holidays by year for better organization
- ✅ Integrated with HolidaySelector.vue component
- ✅ Assignment Rules now support holiday lists via API

#### Implementation Tasks
- [ ] Replace HD Holiday List UI with Holidays doctype list
- [ ] Implement agent-specific holiday lookup
- [ ] Modify SLA timing calculations to account for agent holidays
- [ ] Add carry-forward logic for SLA during holidays
- [ ] Update SLA UI to show holiday-adjusted timings

#### Files to Modify
- `/desk/src/components/Settings/Sla/` (multiple components)
- `/desk/src/stores/sla.ts` (if exists, otherwise create)
- Backend: SLA calculation logic

### 3. Multiple User Assignment UI Component

#### Background
- Similar to existing "Add assignee" functionality
- Allow adding multiple Dynamic User Assignments to rules
- Maintain consistent UI/UX with existing components

#### Implementation Tasks
- [ ] Create MultipleUserAssignmentSelector component
- [ ] Implement search and filter functionality
- [ ] Add bulk selection capabilities
- [ ] Display selected assignments with remove option
- [ ] Integrate with Assignment Rules form

#### Component Structure
```
/desk/src/components/Settings/Assignment Rules/
  - MultipleUserAssignmentSelector.vue
  - UserAssignmentItem.vue
  - UserAssignmentSearch.vue
```

### 4. Fix Subcategory Filter Issue

#### Problem
- Unable to select subcategory from backend
- Need JS filter condition to show only subcategories for selected parent category

#### Implementation Tasks
- [ ] Identify category/subcategory selection components
- [ ] Implement parent-child relationship filtering
- [ ] Add reactive filter updates when parent category changes
- [ ] Test with multiple category levels

## Technical Implementation Details

### API Endpoints Required

1. **Dynamic User Assignment**
   - GET `/api/method/helpdesk.api.dynamic_user_assignment.get_assignments`
   - POST `/api/method/helpdesk.api.dynamic_user_assignment.apply_assignment`

2. **Holidays**
   - GET `/api/method/helpdesk.api.holidays.get_holidays`
   - GET `/api/method/helpdesk.api.holidays.get_agent_holidays`

3. **Category/Subcategory**
   - GET `/api/method/helpdesk.api.categories.get_subcategories`

### Frontend Store Updates

```javascript
// stores/assignmentRules.ts additions
export const dynamicUserAssignments = ref([])
export const selectedHolidays = ref([])

export const fetchDynamicAssignments = async () => {
  // Implementation
}

export const applyDynamicAssignment = async (assignmentId) => {
  // Implementation
}
```

### Component Patterns to Follow

1. **Use existing UI components from frappe-ui**
   - Button, Dialog, ErrorMessage, Dropdown
   - FormControl for form inputs
   - ListView for lists

2. **Follow existing validation patterns**
   ```javascript
   validateAssignmentRule('field_name')
   assignmentRulesErrors.field_name
   ```

3. **Maintain consistent styling**
   - Use Tailwind classes following existing patterns
   - Follow color scheme: ink-gray, surface-gray, outline-gray
   - Maintain spacing: gap-2, mt-4, p-2, etc.

## Development Workflow

### Phase 1: Setup and Analysis
1. Analyze existing codebase structure
2. Understand current assignment rule implementation
3. Map out API requirements

### Phase 2: Backend Integration
1. Update Assignment Rule doctype
2. Create necessary API methods
3. Test API endpoints

### Phase 3: Frontend Components
1. Create Dynamic User Assignment components
2. Implement Holiday selection UI
3. Fix subcategory filtering

### Phase 4: Integration and Testing
1. Integrate all components
2. Test SLA timing with holidays
3. Verify assignment rule execution

### Phase 5: Polish and Documentation
1. Add error handling
2. Implement loading states
3. Update user documentation

## File Structure

```
/desk/src/
├── components/
│   └── Settings/
│       ├── Assignment Rules/
│       │   ├── AssigneeRules.vue (modify)
│       │   ├── AssigneeSearch.vue (modify)
│       │   ├── MultipleUserAssignmentSelector.vue (new)
│       │   ├── UserAssignmentItem.vue (new)
│       │   └── DynamicAssignmentList.vue (new)
│       ├── Holidays/
│       │   ├── HolidaysList.vue (new)
│       │   └── HolidaySelector.vue (new)
│       └── Sla/
│           └── SlaHolidayConfig.vue (new)
├── stores/
│   ├── assignmentRules.ts (modify)
│   ├── holidays.ts (new)
│   └── dynamicAssignments.ts (new)
└── composables/
    └── useHolidayCalculation.ts (new)
```

## Testing Checklist

- [ ] Dynamic User Assignment selection works
- [ ] Multiple assignments can be added/removed
- [ ] Holidays affect SLA timing correctly
- [ ] Subcategory filtering works with parent category
- [ ] Assignment rules execute with new conditions
- [ ] UI maintains consistency across all new components
- [ ] Error states are handled gracefully
- [ ] Loading states are implemented
- [ ] Accessibility requirements are met

## Notes

- Always check `pw_helpdesk` codebase for existing patterns
- Ensure backward compatibility with existing assignment rules
- Consider performance implications for large user/holiday lists
- Implement proper error boundaries for new components