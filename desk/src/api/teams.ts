import { createResource } from "frappe-ui";

export function getTeamsList() {
  return createResource({
    url: "helpdesk.api.team.get_list",
    auto: true,
    transform(data) {
      if (!data || !Array.isArray(data)) return [];
      return data.map(team => ({
        label: typeof team === 'string' ? team : team.name,
        value: typeof team === 'string' ? team : team.name
      }));
    }
  });
}

export function getEmployeeHierarchy(userEmail: string) {
  return createResource({
    url: "pw_helpdesk.customizations.employee_hierarchy_assignment.get_employee_hierarchy_for_user",
    params: { user_email: userEmail },
    auto: false
  });
}