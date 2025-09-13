frappe.ui.form.on('HD Ticket', {
    refresh: function(frm) {
        // Set up category and subcategory filtering
        setup_category_filters(frm);
    },
    
    custom_category: function(frm) {
        // When category changes, clear subcategory and update filter
        frm.set_value('custom_sub_category', '');
        
        // Update subcategory filter
        if (frm.doc.custom_category) {
            frm.set_query('custom_sub_category', function() {
                return {
                    filters: {
                        'is_sub_category': 1,
                        'parent_category': frm.doc.custom_category,
                        'is_active': 1
                    }
                };
            });
            
            // Enable subcategory field
            frm.toggle_enable('custom_sub_category', true);
        } else {
            // Disable subcategory field if no category selected
            frm.toggle_enable('custom_sub_category', false);
        }
    }
});

function setup_category_filters(frm) {
    // Set filter for main category field (only parent categories)
    frm.set_query('custom_category', function() {
        return {
            filters: {
                'is_sub_category': 0,
                'is_active': 1
            }
        };
    });
    
    // Set filter for subcategory field based on selected category
    if (frm.doc.custom_category) {
        frm.set_query('custom_sub_category', function() {
            return {
                filters: {
                    'is_sub_category': 1,
                    'parent_category': frm.doc.custom_category,
                    'is_active': 1
                }
            };
        });
    } else {
        // If no category selected, disable subcategory
        frm.toggle_enable('custom_sub_category', false);
    }
}