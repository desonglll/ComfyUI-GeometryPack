/**
 * ComfyUI GeomPack - VTK.js Side-by-Side Mesh Preview Widget
 * Dual viewport visualization with synchronized cameras
 */

import { app } from "../../../scripts/app.js";

console.log("[GeomPack] Loading VTK.js side-by-side mesh preview extension...");

app.registerExtension({
    name: "geompack.meshpreview.vtk.sidebyside",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "GeomPackPreviewMeshVTKSideBySide") {
            console.log("[GeomPack] Registering Preview Mesh Side-by-Side (VTK) node");

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                console.log("[GeomPack VTK Side-by-Side] Node created, adding widget");

                // Create container for viewer + info panel
                const container = document.createElement("div");
                container.style.width = "100%";
                container.style.height = "100%";
                container.style.display = "flex";
                container.style.flexDirection = "column";
                container.style.backgroundColor = "#2a2a2a";
                container.style.overflow = "hidden";

                // Create iframe for VTK.js viewer
                const iframe = document.createElement("iframe");
                iframe.style.width = "100%";
                iframe.style.flex = "1 1 0";
                iframe.style.minHeight = "0";
                iframe.style.border = "none";
                iframe.style.backgroundColor = "#2a2a2a";

                // Point to side-by-side VTK.js HTML viewer (with cache buster)
                iframe.src = "/extensions/ComfyUI-GeometryPack/viewer_vtk_sidebyside.html?v=" + Date.now();

                // Create mesh info panel
                const infoPanel = document.createElement("div");
                infoPanel.style.backgroundColor = "#1a1a1a";
                infoPanel.style.borderTop = "1px solid #444";
                infoPanel.style.padding = "6px 12px";
                infoPanel.style.fontSize = "10px";
                infoPanel.style.fontFamily = "monospace";
                infoPanel.style.color = "#ccc";
                infoPanel.style.lineHeight = "1.3";
                infoPanel.style.flexShrink = "0";
                infoPanel.style.overflow = "hidden";
                infoPanel.innerHTML = '<span style="color: #888;">Mesh info will appear here after execution</span>';

                // Add iframe and info panel to container
                container.appendChild(iframe);
                container.appendChild(infoPanel);

                // Add widget with required options
                console.log("[GeomPack VTK Side-by-Side] Adding DOM widget");

                const widget = this.addDOMWidget("preview_vtk_sidebyside", "MESH_PREVIEW_VTK_SIDEBYSIDE", container, {
                    getValue() { return ""; },
                    setValue(v) { }
                });

                console.log("[GeomPack VTK Side-by-Side] Widget created:", widget);

                // Wider widget size for dual viewports
                widget.computeSize = () => [768, 640];

                // Store iframe and info panel references
                this.meshViewerIframeVTKSideBySide = iframe;
                this.meshInfoPanelVTKSideBySide = infoPanel;

                // Track iframe load state
                let iframeLoaded = false;
                iframe.addEventListener('load', () => {
                    console.log("[GeomPack VTK Side-by-Side] Iframe loaded");
                    iframeLoaded = true;
                });

                // Listen for messages from iframe
                window.addEventListener('message', async (event) => {
                    // Handle error messages from iframe
                    if (event.data.type === 'MESH_ERROR' && event.data.error) {
                        console.error('[GeomPack VTK Side-by-Side] Error from viewer:', event.data.error, 'Side:', event.data.side);
                        if (infoPanel) {
                            const side = event.data.side || 'unknown';
                            infoPanel.innerHTML = `<div style="color: #ff6b6b; padding: 8px;">Error loading ${side} mesh: ${event.data.error}</div>`;
                        }
                    }
                });

                // Set initial node size (wider for dual viewports)
                this.setSize([768, 640]);
                console.log("[GeomPack VTK Side-by-Side] Node size set to [768, 640]");

                // Handle execution
                const onExecuted = this.onExecuted;
                this.onExecuted = function(message) {
                    console.log("[GeomPack VTK Side-by-Side] onExecuted called with message:", message);
                    onExecuted?.apply(this, arguments);

                    // The message IS the UI data
                    if (message?.mesh_left_file && message?.mesh_right_file) {
                        const filenameLeft = message.mesh_left_file[0];
                        const filenameRight = message.mesh_right_file[0];
                        console.log(`[GeomPack VTK Side-by-Side] Loading meshes - Left: ${filenameLeft}, Right: ${filenameRight}`);

                        // Update mesh info panel with metadata for both meshes
                        const verticesLeft = message.vertex_count_left?.[0] || 'N/A';
                        const verticesRight = message.vertex_count_right?.[0] || 'N/A';
                        const facesLeft = message.face_count_left?.[0] || 'N/A';
                        const facesRight = message.face_count_right?.[0] || 'N/A';

                        const boundsMinLeft = message.bounds_min_left?.[0] || [];
                        const boundsMaxLeft = message.bounds_max_left?.[0] || [];
                        const boundsMinRight = message.bounds_min_right?.[0] || [];
                        const boundsMaxRight = message.bounds_max_right?.[0] || [];

                        const extentsLeft = message.extents_left?.[0] || [];
                        const extentsRight = message.extents_right?.[0] || [];

                        // Format extents
                        let extentsStrLeft = 'N/A';
                        if (extentsLeft.length === 3) {
                            extentsStrLeft = `${extentsLeft.map(v => v.toFixed(2)).join(' × ')}`;
                        }

                        let extentsStrRight = 'N/A';
                        if (extentsRight.length === 3) {
                            extentsStrRight = `${extentsRight.map(v => v.toFixed(2)).join(' × ')}`;
                        }

                        // Build info HTML with two columns
                        let infoHTML = `
                            <div style="display: grid; grid-template-columns: auto 1fr 1fr; gap: 2px 12px;">
                                <span style="color: #888;"></span>
                                <span style="color: #999; font-weight: bold; border-bottom: 1px solid #333;">Left Mesh</span>
                                <span style="color: #999; font-weight: bold; border-bottom: 1px solid #333;">Right Mesh</span>

                                <span style="color: #888;">Vertices:</span>
                                <span>${verticesLeft.toLocaleString()}</span>
                                <span>${verticesRight.toLocaleString()}</span>

                                <span style="color: #888;">Faces:</span>
                                <span>${facesLeft.toLocaleString()}</span>
                                <span>${facesRight.toLocaleString()}</span>

                                <span style="color: #888;">Extents:</span>
                                <span style="font-size: 9px;">${extentsStrLeft}</span>
                                <span style="font-size: 9px;">${extentsStrRight}</span>
                        `;

                        // Add watertight info if available
                        if (message.is_watertight_left !== undefined && message.is_watertight_right !== undefined) {
                            const watertightLeft = message.is_watertight_left[0] ? 'Yes' : 'No';
                            const watertightRight = message.is_watertight_right[0] ? 'Yes' : 'No';
                            const colorLeft = message.is_watertight_left[0] ? '#6c6' : '#c66';
                            const colorRight = message.is_watertight_right[0] ? '#6c6' : '#c66';
                            infoHTML += `
                                <span style="color: #888;">Watertight:</span>
                                <span style="color: ${colorLeft};">${watertightLeft}</span>
                                <span style="color: ${colorRight};">${watertightRight}</span>
                            `;
                        }

                        infoHTML += '</div>';

                        infoPanel.innerHTML = infoHTML;

                        // ComfyUI serves output files via /view API endpoint
                        const filepathLeft = `/view?filename=${encodeURIComponent(filenameLeft)}&type=output&subfolder=`;
                        const filepathRight = `/view?filename=${encodeURIComponent(filenameRight)}&type=output&subfolder=`;

                        // Function to send message
                        const sendMessage = () => {
                            if (iframe.contentWindow) {
                                console.log(`[GeomPack VTK Side-by-Side] Sending postMessage to iframe`);
                                console.log(`  Left: ${filepathLeft}`);
                                console.log(`  Right: ${filepathRight}`);
                                iframe.contentWindow.postMessage({
                                    type: "LOAD_MESHES",
                                    leftFilepath: filepathLeft,
                                    rightFilepath: filepathRight,
                                    timestamp: Date.now()
                                }, "*");
                            } else {
                                console.error("[GeomPack VTK Side-by-Side] Iframe contentWindow not available");
                            }
                        };

                        // Send message after iframe is loaded
                        if (iframeLoaded) {
                            console.log("[GeomPack VTK Side-by-Side] Iframe already loaded, sending immediately");
                            sendMessage();
                        } else {
                            console.log("[GeomPack VTK Side-by-Side] Waiting for iframe to load...");
                            setTimeout(sendMessage, 500);
                        }
                    } else {
                        console.log("[GeomPack VTK Side-by-Side] Missing mesh files in message data. Keys:", Object.keys(message || {}));
                    }
                };

                return r;
            };
        }
    }
});

console.log("[GeomPack] VTK.js side-by-side mesh preview extension registered");
