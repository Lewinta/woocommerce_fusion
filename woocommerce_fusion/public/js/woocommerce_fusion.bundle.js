(function() {
    // Wait for frappe to be ready
    $(document).ready(function() {
        // Only initialize if frappe is available and we're not in a dialog
        if (typeof frappe !== 'undefined' && !window.location.pathname.includes('/desk')) {
            setTimeout(initFloatingButton, 1000);
        } else if (typeof frappe !== 'undefined') {
            initFloatingButton();
        }
    });

    function initFloatingButton() {
        // Check if button already exists
        if (document.getElementById('wc-fusion-floating-btn')) {
            return;
        }

        // Create floating button
        const floatingBtn = document.createElement('div');
        floatingBtn.id = 'wc-fusion-floating-btn';
        floatingBtn.innerHTML = `
            <div class="floating-btn-content">
                <svg class="scan-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 7V5C3 3.89543 3.89543 3 5 3H7M3 17V19C3 20.1046 3.89543 21 5 21H7M21 7V5C21 3.89543 20.1046 3 19 3H17M21 17V19C21 20.1046 20.1046 21 19 21H17M12 8V16M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="btn-text">Scan</span>
            </div>
        `;

        // Add styles
        const styles = `
            #wc-fusion-floating-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 70px;
                height: 70px;
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 50%;
                cursor: pointer;
                z-index: 9999;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 
                           0 2px 8px rgba(0, 0, 0, 0.08),
                           inset 0 1px 0 rgba(255, 255, 255, 0.1);
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                user-select: none;
            }

            #wc-fusion-floating-btn:hover {
                width: 120px;
                border-radius: 35px;
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-2px);
                box-shadow: 0 16px 48px rgba(0, 0, 0, 0.18),
                           0 4px 16px rgba(0, 0, 0, 0.12),
                           inset 0 1px 0 rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }

            #wc-fusion-floating-btn:active {
                transform: translateY(0px) scale(0.95);
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            }

            .floating-btn-content {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0;
                color: #1e293b;
                font-weight: 600;
                font-size: 14px;
                white-space: nowrap;
                width: 100%;
                height: 100%;
                position: relative;
                transition: gap 0.3s ease;
            }

            #wc-fusion-floating-btn:hover .floating-btn-content {
                gap: 8px;
            }

            .scan-icon {
                transition: all 0.3s ease;
                flex-shrink: 0;
                display: block;
                margin: 0;
                transform: scale(1);
            }

            #wc-fusion-floating-btn:hover .scan-icon {
                transform: scale(1.1);
            }

            .btn-text {
                opacity: 0;
                transform: translateX(-10px);
                transition: all 0.3s ease;
                overflow: hidden;
                width: 0;
                white-space: nowrap;
            }

            #wc-fusion-floating-btn:hover .btn-text {
                opacity: 1;
                transform: translateX(0);
                width: auto;
            }

            /* Animation for initial appearance */
            @keyframes bounceIn {
                0% {
                    transform: scale(0) rotate(180deg);
                    opacity: 0;
                }
                50% {
                    transform: scale(1.2) rotate(90deg);
                    opacity: 0.8;
                }
                100% {
                    transform: scale(1) rotate(0deg);
                    opacity: 1;
                }
            }

            #wc-fusion-floating-btn {
                animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            }

            /* Dark mode support - Enhanced styling */
            @media (prefers-color-scheme: dark) {
                #wc-fusion-floating-btn {
                    background: rgba(15, 23, 42, 0.7);
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                               0 2px 8px rgba(0, 0, 0, 0.3),
                               inset 0 1px 0 rgba(255, 255, 255, 0.05);
                }
                
                #wc-fusion-floating-btn:hover {
                    background: rgba(30, 41, 59, 0.8);
                    border: 1px solid rgba(148, 163, 184, 0.3);
                    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5),
                               0 4px 16px rgba(0, 0, 0, 0.4),
                               inset 0 1px 0 rgba(255, 255, 255, 0.08);
                }
                
                .floating-btn-content {
                    color: #e2e8f0;
                }
                
                .scan-icon {
                    filter: brightness(1.1);
                }
            }

            /* Mobile responsive */
            @media (max-width: 768px) {
                #wc-fusion-floating-btn {
                    bottom: 20px;
                    left: 20px;
                    width: 60px;
                    height: 60px;
                }
                
                #wc-fusion-floating-btn:hover {
                    width: 60px;
                    border-radius: 50%;
                }
                
                .btn-text {
                    display: none;
                }
                
                .scan-icon {
                    width: 20px;
                    height: 20px;
                }
            }
        `;

        // Add styles to head
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);

        // Add event listener
        floatingBtn.addEventListener('click', openScanDialog);

        // Add to body
        document.body.appendChild(floatingBtn);
    }

    function openScanDialog() {
        // Create and show the dialog
        const dialog = new frappe.ui.Dialog({
            title: __('Quick Scan & Document Selection'),
            size: 'large',
            fields: [
                {
                    fieldtype: 'Section Break',
                    label: __('Document Selection')
                },
                {
                    fieldtype: 'Link',
                    fieldname: 'doctype',
                    label: __('Select Document Type'),
                    options: 'DocType',
                    reqd: 1,
                    description: __('Choose the type of document you want to work with'),
                    get_query: function() {
                        return {
                            filters: {
                                'issingle': 0,
                                'istable': 0,
                                'module': ['not in', ['Core']]
                            }
                        };
                    },
                    onchange: function() {
                        const selectedDoctype = dialog.get_value('doctype');
                        if (selectedDoctype) {
                            // Update the scan field description based on selected doctype
                            dialog.set_df_property('barcode_data', 'description', 
                                __('Scan or enter barcode for {0}', [selectedDoctype]));
                        }
                    }
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'HTML',
                    fieldname: 'doctype_info',
                    options: '<div class="text-muted" style="padding: 10px; border-radius: 4px; background-color: #f8f9fa;"><i class="fa fa-info-circle"></i> Select a document type to enable scanning functionality</div>'
                },
                {
                    fieldtype: 'Section Break',
                    label: __('Barcode Scanner')
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'barcode_data',
                    label: __('Scan Barcode'),
                    options: 'Barcode',
                    description: __('Use the scanner or type the barcode manually'),
                    onchange: function() {
                        const barcode = dialog.get_value('barcode_data');
                        const doctype = dialog.get_value('doctype');
                        
                        if (barcode && doctype) {
                            // Process the scanned barcode
                            processScannedBarcode(barcode, doctype, dialog);
                        }
                    }
                },
                {
                    fieldtype: 'Column Break'
                },
                {
                    fieldtype: 'Button',
                    fieldname: 'camera_scan',
                    label: __('Open Camera Scanner'),
                    click: function() {
                        openCameraScanner(dialog);
                    }
                },
                {
                    fieldtype: 'Section Break'
                },
                {
                    fieldtype: 'HTML',
                    fieldname: 'scan_results',
                    options: '<div id="scan-results-area" style="min-height: 100px; padding: 15px; border: 1px dashed #d1d8dd; border-radius: 4px; background-color: #fafbfc;"><div class="text-center text-muted"><i class="fa fa-search"></i><br><br>Scan results will appear here</div></div>'
                }
            ],
            primary_action_label: __('Process Scan'),
            primary_action: function() {
                const values = dialog.get_values();
                if (values.doctype && values.barcode_data) {
                    processScan(values, dialog);
                } else {
                    frappe.msgprint(__('Please select a document type and scan a barcode'));
                }
            },
            secondary_action_label: __('Close'),
            secondary_action: function() {
                dialog.hide();
            }
        });

        // Show the dialog
        dialog.show();

        // Focus on doctype field
        setTimeout(() => {
            dialog.fields_dict.doctype.$input.focus();
        }, 500);
    }

    function openCameraScanner(dialog) {
        // Use Frappe's built-in scanner if available
        if (frappe.ui.Scanner) {
            new frappe.ui.Scanner({
                dialog: true,
                multiple: false,
                on_scan: function(data) {
                    if (data && data.result && data.result.text) {
                        dialog.set_value('barcode_data', data.result.text);
                        // Trigger the onchange event
                        dialog.fields_dict.barcode_data.$input.trigger('change');
                    }
                }
            });
        } else {
            frappe.msgprint(__('Camera scanner is not available. Please enter the barcode manually.'));
        }
    }

    function processScannedBarcode(barcode, doctype, dialog) {
        // Update the results area
        const resultsArea = document.getElementById('scan-results-area');
        if (resultsArea) {
            resultsArea.innerHTML = `
                <div class="scan-result-item">
                    <div class="d-flex align-items-center">
                        <div class="mr-3">
                            <i class="fa fa-barcode text-primary" style="font-size: 24px;"></i>
                        </div>
                        <div class="flex-1">
                            <strong>Scanned:</strong> ${barcode}<br>
                            <small class="text-muted">Document Type: ${doctype}</small>
                        </div>
                        <div class="ml-3">
                            <span class="badge badge-success">Ready</span>
                        </div>
                    </div>
                </div>
            `;
        }

        // You can add more processing logic here
        // For example, search for existing records, validate barcode format, etc.
    }

    function processScan(values, dialog) {
        // Show loading
        dialog.set_message(__('Processing scan...'));
        
        // Simulate processing (replace with actual logic)
        setTimeout(() => {
            frappe.show_alert({
                message: __('Scan processed successfully! Barcode: {0}, DocType: {1}', [values.barcode_data, values.doctype]),
                indicator: 'green'
            });
            
            // You can add your custom logic here
            // For example:
            // - Search for existing records with this barcode
            // - Create new records
            // - Update inventory
            // - Navigate to relevant forms
            
            dialog.hide();
        }, 1500);
    }

    // CSS for enhanced styling
    const additionalStyles = `
        .scan-result-item {
            padding: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            background: white;
            margin-bottom: 8px;
            transition: all 0.2s ease;
        }
        
        .scan-result-item:hover {
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-color: #3b82f6;
        }
        
        .dialog .modal-body {
            min-height: 400px;
        }
        
        /* Enhanced dialog styling */
        .frappe-dialog .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom: none;
        }
        
        .frappe-dialog .modal-header .modal-title {
            color: white;
        }
        
        .frappe-dialog .btn-modal-close {
            color: white;
            opacity: 0.8;
        }
        
        .frappe-dialog .btn-modal-close:hover {
            opacity: 1;
        }
    `;

    // Add additional styles
    const additionalStyleSheet = document.createElement('style');
    additionalStyleSheet.textContent = additionalStyles;
    document.head.appendChild(additionalStyleSheet);

})();
