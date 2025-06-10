(()=>{(function(){$(document).ready(function(){typeof frappe!="undefined"&&!window.location.pathname.includes("/desk")?setTimeout(a,1e3):typeof frappe!="undefined"&&a()});function a(){if(document.getElementById("wc-fusion-floating-btn"))return;let e=document.createElement("div");e.id="wc-fusion-floating-btn",e.innerHTML=`
            <div class="floating-btn-content">
                <svg class="scan-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 7V5C3 3.89543 3.89543 3 5 3H7M3 17V19C3 20.1046 3.89543 21 5 21H7M21 7V5C21 3.89543 20.1046 3 19 3H17M21 17V19C21 20.1046 20.1046 21 19 21H17M12 8V16M8 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span class="btn-text">Scan</span>
            </div>
        `;let t=`
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
        `,n=document.createElement("style");n.textContent=t,document.head.appendChild(n),e.addEventListener("click",r),document.body.appendChild(e)}function r(){let e=new frappe.ui.Dialog({title:__("Quick Scan & Document Selection"),size:"large",fields:[{fieldtype:"Section Break",label:__("Document Selection")},{fieldtype:"Link",fieldname:"doctype",label:__("Select Document Type"),options:"DocType",reqd:1,description:__("Choose the type of document you want to work with"),get_query:function(){return{filters:{issingle:0,istable:0,module:["not in",["Core"]]}}},onchange:function(){let t=e.get_value("doctype");t&&e.set_df_property("barcode_data","description",__("Scan or enter barcode for {0}",[t]))}},{fieldtype:"Column Break"},{fieldtype:"HTML",fieldname:"doctype_info",options:'<div class="text-muted" style="padding: 10px; border-radius: 4px; background-color: #f8f9fa;"><i class="fa fa-info-circle"></i> Select a document type to enable scanning functionality</div>'},{fieldtype:"Section Break",label:__("Barcode Scanner")},{fieldtype:"Data",fieldname:"barcode_data",label:__("Scan Barcode"),options:"Barcode",description:__("Use the scanner or type the barcode manually"),onchange:function(){let t=e.get_value("barcode_data"),n=e.get_value("doctype");t&&n&&c(t,n,e)}},{fieldtype:"Column Break"},{fieldtype:"Button",fieldname:"camera_scan",label:__("Open Camera Scanner"),click:function(){s(e)}},{fieldtype:"Section Break"},{fieldtype:"HTML",fieldname:"scan_results",options:'<div id="scan-results-area" style="min-height: 100px; padding: 15px; border: 1px dashed #d1d8dd; border-radius: 4px; background-color: #fafbfc;"><div class="text-center text-muted"><i class="fa fa-search"></i><br><br>Scan results will appear here</div></div>'}],primary_action_label:__("Process Scan"),primary_action:function(){let t=e.get_values();t.doctype&&t.barcode_data?d(t,e):frappe.msgprint(__("Please select a document type and scan a barcode"))},secondary_action_label:__("Close"),secondary_action:function(){e.hide()}});e.show(),setTimeout(()=>{e.fields_dict.doctype.$input.focus()},500)}function s(e){frappe.ui.Scanner?new frappe.ui.Scanner({dialog:!0,multiple:!1,on_scan:function(t){t&&t.result&&t.result.text&&(e.set_value("barcode_data",t.result.text),e.fields_dict.barcode_data.$input.trigger("change"))}}):frappe.msgprint(__("Camera scanner is not available. Please enter the barcode manually."))}function c(e,t,n){let i=document.getElementById("scan-results-area");i&&(i.innerHTML=`
                <div class="scan-result-item">
                    <div class="d-flex align-items-center">
                        <div class="mr-3">
                            <i class="fa fa-barcode text-primary" style="font-size: 24px;"></i>
                        </div>
                        <div class="flex-1">
                            <strong>Scanned:</strong> ${e}<br>
                            <small class="text-muted">Document Type: ${t}</small>
                        </div>
                        <div class="ml-3">
                            <span class="badge badge-success">Ready</span>
                        </div>
                    </div>
                </div>
            `)}function d(e,t){t.set_message(__("Processing scan...")),setTimeout(()=>{frappe.show_alert({message:__("Scan processed successfully! Barcode: {0}, DocType: {1}",[e.barcode_data,e.doctype]),indicator:"green"}),t.hide()},1500)}let l=`
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
    `,o=document.createElement("style");o.textContent=l,document.head.appendChild(o)})();})();
//# sourceMappingURL=woocommerce_fusion.bundle.IV4HHT4O.js.map
