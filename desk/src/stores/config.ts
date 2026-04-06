import { socket } from "@/socket";
import { createResource } from "frappe-ui";
import { defineStore } from "pinia";
import { computed, ComputedRef } from "vue";

export const useConfigStore = defineStore("config", () => {
  const configResource = createResource({
    url: "helpdesk.api.config.get_config",
    auto: true,
  });

  const config = computed(() => configResource.data || {});
  const brandName = computed(() => config.value.brand_name);
  const brandLogo = computed(() => config.value.brand_logo);
  const favicon = computed(() => config.value.favicon);

  const teamRestrictionApplied = computed(
    () => !!parseInt(config.value.restrict_tickets_by_agent_group)
  );
  const disableGlobalScopeForSavedReplies = computed(
    () => !!parseInt(config.value.disable_saved_replies_global_scope)
  );
  const assignWithinTeam = computed(
    () => !!parseInt(config.value.assign_within_team)
  );
  const skipEmailWorkflow: ComputedRef<boolean> = computed(
    () => !!parseInt(config.value.skip_email_workflow)
  );
  const preferKnowledgeBase = computed(
    () => !!parseInt(config.value.prefer_knowledge_base)
  );
  const isFeedbackMandatory = computed(
    () => !!parseInt(config.value.is_feedback_mandatory)
  );
  const enableCommentReactions = computed(
    () => !!parseInt(config.value.enable_comment_reactions)
  );
  const enableOurServices = computed(() => {
    const val = config.value.enable_our_services;
    return val === undefined || val === null ? true : !!parseInt(val);
  });
  const enableBuyServices = computed(() => {
    const val = config.value.enable_buy_services;
    return val === undefined || val === null ? true : !!parseInt(val);
  });
  const enableWiki = computed(() => {
    const val = config.value.enable_wiki;
    return val === undefined || val === null ? true : !!parseInt(val);
  });
  const enableSupportPlan = computed(() => {
    const val = config.value.enable_support_plan;
    if (val === undefined || val === null) return false;
    if (typeof val === "boolean") return val;
    if (typeof val === "number") return val === 1;
    return val === "1" || val.toLowerCase() === "true";
  });

  socket.on("helpdesk:settings-updated", () => configResource.reload());

  return {
    configResource,
    brandName,
    brandLogo,
    favicon,
    config,
    preferKnowledgeBase,
    skipEmailWorkflow,
    isFeedbackMandatory,
    teamRestrictionApplied,
    assignWithinTeam,
    disableGlobalScopeForSavedReplies,
    enableCommentReactions,
    enableOurServices,
    enableBuyServices,
    enableWiki,
    enableSupportPlan,
  };
});
