/*
Based on Preview Any - original implement from https://github.com/rgthree/rgthree-comfy/blob/main/py/display_any.py
 */

import { app } from "../../scripts/app.js";

function createContainer() {
  const container = document.createElement('div')
  container.classList.add('comfy-img-preview')
  return container
}

app.registerExtension({
  name: 'QTools.QPreviewLatent',
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name === 'QPreviewLatent') {
      const onNodeCreated = nodeType.prototype.onNodeCreated

      nodeType.prototype.onNodeCreated = function () {
        onNodeCreated ? onNodeCreated.apply(this, []) : undefined
        let summary = document.createElement('div')
        summary.style.overflow="auto";

        this.addDOMWidget("summary", 'image', summary, {   })
      }

      const onExecuted = nodeType.prototype.onExecuted

      nodeType.prototype.onExecuted = function (message) {
        onExecuted === null || onExecuted === void 0
          ? void 0
          : onExecuted.apply(this, [message])

        const previewWidget = this.widgets?.find((w) => w.name === 'summary')
        if (previewWidget) {
          previewWidget.element.innerHTML = message.html[0]
        }
      }
    }
  }
})
