(() => {
  // ../woocommerce_fusion/woocommerce_fusion/public/js/woocommerce_fusion.bundle.js
  (function() {
    $(document).ready(function() {
      if (typeof frappe !== "undefined" && !window.location.pathname.includes("/desk")) {
        setTimeout(initFloatingButton, 1e3);
      } else if (typeof frappe !== "undefined") {
        initFloatingButton();
      }
    });
    function initFloatingButton() {
      if (document.getElementById("wc-fusion-floating-btn")) {
        return;
      }
      const floatingBtn = document.createElement("div");
      floatingBtn.id = "wc-fusion-floating-btn";
      floatingBtn.innerHTML = `
            <div class="floating-btn-content">
                <svg class="scan-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 7V5C3 3.89543 3.89543 3 5 3H7M3 17V19C3 20.1046 3.89543 21 5 21H7M21 7V5C21 3.89543 20.1046 3 19 3H17M21 17V19C21 20.1046 20.1046 21 19 21H17M12 8V16M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="btn-text">Scan</span>
            </div>
        `;
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
      const styleSheet = document.createElement("style");
      styleSheet.textContent = styles;
      document.head.appendChild(styleSheet);
      floatingBtn.addEventListener("click", openScanDialog);
      document.body.appendChild(floatingBtn);
    }
    function openScanDialog() {
      const dialog = new frappe.ui.Dialog({
        title: __("Quick Scan & Document Selection"),
        size: "large",
        fields: [
          {
            fieldtype: "Select",
            fieldname: "doctype",
            label: __("Select Document Type"),
            options: "\nSales Order\nPick List\nItem",
            reqd: 0
          },
          {
            fieldtype: "Data",
            fieldname: "document",
            label: __("Scan Document"),
            options: "Barcode",
            onchange: () => {
              const { doctype, document: document2 } = dialog.get_values();
              if (!document2)
                return;
              goToDocument(document2, doctype);
            }
          }
        ],
        primary_action_label: __("Open Document"),
        primary_action: function() {
          const values = dialog.get_values();
          if (values.doctype && values.barcode_data) {
            processScan(values, dialog);
          } else {
            frappe.msgprint(__("Please select a document type and scan a barcode"));
          }
        },
        secondary_action_label: __("Close"),
        secondary_action: function() {
          dialog.hide();
        }
      });
      dialog.show();
      setTimeout(() => {
        dialog.fields_dict.doctype.$input.focus();
      }, 500);
    }
    function openCameraScanner(dialog) {
      if (frappe.ui.Scanner) {
        new frappe.ui.Scanner({
          dialog: true,
          multiple: false,
          on_scan: function(data) {
            if (data && data.result && data.result.text) {
              dialog.set_value("barcode_data", data.result.text);
              dialog.fields_dict.barcode_data.$input.trigger("change");
            }
          }
        });
      } else {
        frappe.msgprint(__("Camera scanner is not available. Please enter the barcode manually."));
      }
    }
    function processScannedBarcode(barcode, doctype, dialog) {
      const resultsArea = document.getElementById("scan-results-area");
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
    }
    function processScan(values, dialog) {
      dialog.set_message(__("Processing scan..."));
      setTimeout(() => {
        frappe.show_alert({
          message: __("Scan processed successfully! Barcode: {0}, DocType: {1}", [values.barcode_data, values.doctype]),
          indicator: "green"
        });
        dialog.hide();
      }, 1500);
    }
    function goToDocument(name, doctype) {
      const method = "woocommerce_fusion.utils.get_document";
      const opts = {
        method,
        args: { name, doctype }
      };
      frappe.call(opts).then(({ message }) => {
        if (message) {
          frappe.set_route("Form", message.doctype, message.name);
        } else {
          const msg = `${name} does not exist`;
          cur_dialog.set_df_property("document", "description", msg);
        }
      });
    }
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
    const additionalStyleSheet = document.createElement("style");
    additionalStyleSheet.textContent = additionalStyles;
    document.head.appendChild(additionalStyleSheet);
  })();
})();
//# sourceMappingURL=woocommerce_fusion.bundle.WRZTUI6S.js.map
