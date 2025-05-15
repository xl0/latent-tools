/*
Based on Preview Any - original implement from https://github.com/rgthree/rgthree-comfy/blob/main/py/display_any.py
 */

import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

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

        console.log(nodeData);

        // const svg = new SVGAElement();

        // let img_div = createContainer();
        let summary = document.createElement('div')
        // let img = new Image();
        // img.src="https://cataas.com/cat"
        // img_div.appendChild(img);
        summary.style.overflow="auto";
        // summary.innerHTML
        // img_div.firstChild

        // img.classList.add('comfy-markdown')
        // const textarea = document.createElement('textarea')
        // inputEl.append(textarea)

        this.addDOMWidget("summary", 'image', summary, {   })
        // widget.inputEl = inputEl
        // widget.options.minNodeSize = [400, 200]


        // const showValueWidget = ComfyWidgets['MARKDOWN'](
        //   this,
        //   'md',
        //   ['MARKDOWN', { multiline: true,  }],
        //   app
        // ).widget

        // showValueWidget.element.readOnly = true

        // showValueWidget.serialize = false
      }

      const onExecuted = nodeType.prototype.onExecuted

      nodeType.prototype.onExecuted = function (message) {
        onExecuted === null || onExecuted === void 0
          ? void 0
          : onExecuted.apply(this, [message])

        const previewWidget = this.widgets?.find((w) => w.name === 'summary')

        console.log(message);
        console.log(this);
        if (previewWidget) {
          previewWidget.element.innerHTML = message.html[0]
        }
      }
    }
  }
})
