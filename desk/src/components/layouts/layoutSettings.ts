import LucideBookOpen from "~icons/lucide/book-open";
import LucideBriefcase from "~icons/lucide/briefcase";
import LucideContact2 from "~icons/lucide/contact-2";
import LucideRocket from "~icons/lucide/rocket";
import LucideShoppingCart from "~icons/lucide/shopping-cart";
import LucideTicket from "~icons/lucide/ticket";
import LucideCompass from "~icons/lucide/compass";
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
    label: __("Onboarding"),
    icon: LucideCompass,
    onClick: () => {
      window.location.href = "/onboarding";
    },
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
    label: __("Buy Services"),
    icon: LucideShoppingCart,
    to: "BuyServicesAgent",
  },
  {
    label: __("Our Services"),
    icon: LucideBriefcase,
    to: "OurServicesAgent",
  },
];

export const customerPortalSidebarOptions = [
  {
    label: __("Tickets"),
    icon: LucideTicket,
    to: "TicketsCustomer",
  },
  {
    label: __("Onboarding"),
    icon: LucideCompass,
    onClick: () => {
      window.location.href = "/onboarding";
    },
  },
  {
    label: __("Get Started"),
    icon: LucideRocket,
    to: "CustomerKnowledgeBase",
  },
  {
    label: __("Buy Services"),
    icon: LucideShoppingCart,
    to: "BuyServices",
  },
  {
    label: __("Our Services"),
    icon: LucideBriefcase,
    to: "OurServices",
  },
];
