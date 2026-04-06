import LucideBriefcase from "~icons/lucide/briefcase";
import LucideContact2 from "~icons/lucide/contact-2";
import LucideFileText from "~icons/lucide/file-text";
import LucideRocket from "~icons/lucide/rocket";
import LucideShoppingCart from "~icons/lucide/shopping-cart";
import LucideTicket from "~icons/lucide/ticket";
import { OrganizationsIcon } from "../icons";
import PhoneIcon from "../icons/PhoneIcon.vue";
import { __ } from "@/translation";

export const agentPortalSidebarOptions = [
  {
    label: __("Tickets"),
    icon: LucideTicket,
    to: "TicketsAgent",
  },
  {
    label: __("Get Started"),
    icon: LucideRocket,
    to: "AgentKnowledgeBase",
  },
  {
    label: __("Customers"),
    icon: OrganizationsIcon,
    to: "CustomerList",
  },
  {
    label: __("Contacts"),
    icon: LucideContact2,
    to: "ContactList",
  },
  {
    label: __("Call Logs"),
    icon: PhoneIcon,
    to: "CallLogs",
  },
  {
    label: __("Our Services"),
    icon: LucideBriefcase,
    to: "OurServicesAgent",
  },
  {
    label: __("Support Plan"),
    icon: LucideFileText,
    to: "SupportPlanAgent",
  },
  {
    label: __("Buy Services"),
    icon: LucideShoppingCart,
    to: "BuyServicesAgent",
  },
];

export const customerPortalSidebarOptions = [
  {
    label: __("Tickets"),
    icon: LucideTicket,
    to: "TicketsCustomer",
  },
  {
    label: __("Get Started"),
    icon: LucideRocket,
    to: "CustomerKnowledgeBase",
  },
  {
    label: __("Our Services"),
    icon: LucideBriefcase,
    to: "OurServices",
  },
  {
    label: __("Support Plan"),
    icon: LucideFileText,
    to: "SupportPlan",
  },
  {
    label: __("Buy Services"),
    icon: LucideShoppingCart,
    to: "BuyServices",
  },
];
