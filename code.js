// Figma Plugin Code
// Twizer BG Pro - Background Removal, Watermark Removal, Upscale

figma.showUI(__html__, { width: 380, height: 580 });

// Secili node'u al
function getSelectedNode() {
  const selection = figma.currentPage.selection;
  
  if (selection.length === 0) {
    figma.ui.postMessage({
      type: 'error',
      message: 'Lutfen bir gorsel secin.'
    });
    return null;
  }
  
  const node = selection[0];
  
  // Desteklenen node tipleri
  const supportedTypes = ['RECTANGLE', 'FRAME', 'COMPONENT', 'INSTANCE', 'GROUP'];
  
  if (!supportedTypes.includes(node.type)) {
    figma.ui.postMessage({
      type: 'error',
      message: 'Bu islem sadece gorsellerde calisir.'
    });
    return null;
  }
  
  return node;
}

// Node'dan gorseli al
async function getImageFromNode(node) {
  try {
    const imageBytes = await node.exportAsync({
      format: 'PNG',
      constraint: { type: 'SCALE', value: 2 }
    });
    
    const bytes = Array.from(imageBytes);
    
    return {
      bytes: bytes,
      nodeId: node.id,
      nodeName: node.name,
      width: node.width,
      height: node.height
    };
  } catch (error) {
    console.error('getImageFromNode hatasi:', error);
    throw new Error('Gorsel alinamadi.');
  }
}

// Base64 decode
function base64ToUint8Array(base64) {
  const base64Chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  
  let paddingCount = 0;
  if (base64[base64.length - 1] === '=') {
    paddingCount++;
    if (base64[base64.length - 2] === '=') {
      paddingCount++;
    }
  }
  
  const len = base64.length;
  const bufferLength = Math.floor((len * 3) / 4) - paddingCount;
  
  if (bufferLength <= 0) {
    throw new Error('Gecersiz gorsel verisi');
  }
  
  const bytes = new Uint8Array(bufferLength);
  let p = 0;
  
  for (let i = 0; i < len - paddingCount; i += 4) {
    const char1 = base64[i] || 'A';
    const char2 = base64[i + 1] || 'A';
    const char3 = base64[i + 2] || 'A';
    const char4 = base64[i + 3] || 'A';
    
    const encoded1 = base64Chars.indexOf(char1);
    const encoded2 = base64Chars.indexOf(char2);
    const encoded3 = char3 === '=' ? -1 : base64Chars.indexOf(char3);
    const encoded4 = char4 === '=' ? -1 : base64Chars.indexOf(char4);
    
    if (encoded1 === -1 || encoded2 === -1) {
      throw new Error('Gecersiz gorsel verisi');
    }
    
    if (p < bufferLength) {
      bytes[p++] = (encoded1 << 2) | (encoded2 >> 4);
    }
    if (encoded3 !== -1 && p < bufferLength) {
      bytes[p++] = ((encoded2 & 15) << 4) | (encoded3 >> 2);
    }
    if (encoded4 !== -1 && p < bufferLength) {
      bytes[p++] = ((encoded3 & 3) << 6) | encoded4;
    }
  }
  
  return bytes;
}

// Gorseli Figma'ya uygula
async function applyImageToNode(imageBase64, nodeId, nodeName, width, height, isUpscaled = false) {
  try {
    if (!imageBase64 || typeof imageBase64 !== 'string') {
      throw new Error('Gorsel verisi gecersiz');
    }
    
    // Base64 temizle
    let base64Data = imageBase64;
    if (base64Data.includes('data:image')) {
      base64Data = base64Data.replace(/^data:image\/\w+;base64,/, '');
    }
    base64Data = base64Data.trim().replace(/\s/g, '');
    
    if (!base64Data || base64Data.length === 0) {
      throw new Error('Gorsel verisi bos');
    }
    
    // Base64 decode
    let bytes;
    try {
      bytes = base64ToUint8Array(base64Data);
    } catch (decodeError) {
      console.error('Base64 decode hatasi:', decodeError);
      throw new Error('Gorsel isleme hatasi');
    }
    
    if (!bytes || bytes.length === 0) {
      throw new Error('Gorsel verisi bos');
    }
    
    // Upscale icin buyuk gorsel kontrolu
    if (isUpscaled && bytes.length > 50 * 1024 * 1024) {
      console.warn('Upscaled gorsel cok buyuk');
    }
    
    // Figma image olustur
    let image;
    try {
      image = figma.createImage(bytes);
    } catch (imageError) {
      console.error('Figma createImage hatasi:', imageError);
      if (imageError.message && imageError.message.includes('too large') && isUpscaled) {
        throw new Error('Gorsel cok buyuk. Daha kucuk gorsel deneyin.');
      }
      throw new Error('Gorsel olusturulamadi');
    }
    
    // Node'u bul
    const node = await figma.getNodeByIdAsync(nodeId);
    if (!node) {
      throw new Error('Layer bulunamadi, tekrar secin');
    }
    
    // Fill uygula
    if (node.type === 'RECTANGLE' || 
        node.type === 'FRAME' || 
        node.type === 'COMPONENT' ||
        node.type === 'INSTANCE') {
      
      node.fills = [{
        type: 'IMAGE',
        imageHash: image.hash,
        scaleMode: 'FILL'
      }];
      
      if (width && height && width > 0 && height > 0) {
        try {
          node.resize(width, height);
        } catch (resizeError) {
          console.warn('Resize hatasi:', resizeError);
        }
      }
    } else if (node.type === 'GROUP') {
      const rect = figma.createRectangle();
      rect.name = (nodeName || 'Image') + ' (Processed)';
      rect.fills = [{
        type: 'IMAGE',
        imageHash: image.hash,
        scaleMode: 'FILL'
      }];
      
      if (width && height && width > 0 && height > 0) {
        rect.resize(width, height);
      }
      
      if (node.parent && node.parent.type !== 'PAGE') {
        node.parent.appendChild(rect);
      } else {
        figma.currentPage.appendChild(rect);
      }
      rect.x = node.x;
      rect.y = node.y;
      
      figma.currentPage.selection = [rect];
    } else {
      throw new Error('Desteklenmeyen layer tipi');
    }
    
    figma.ui.postMessage({
      type: 'applied',
      message: 'Basariyla uygulandi!'
    });
    
  } catch (error) {
    const errorMsg = error.message || 'Bilinmeyen hata';
    console.error('applyImageToNode hatasi:', error);
    figma.ui.postMessage({
      type: 'error',
      message: 'Islem basarisiz oldu, tekrar deneyin.'
    });
  }
}

// UI mesajlarini dinle
figma.ui.onmessage = async (msg) => {
  // Gorsel alma istegi
  if (msg.type === 'get-image') {
    const node = getSelectedNode();
    if (!node) return;
    
    try {
      const imageData = await getImageFromNode(node);
      figma.ui.postMessage({
        type: 'image-ready',
        data: imageData,
        mode: msg.mode || 'background' // background | watermark | upscale
      });
    } catch (error) {
      console.error('get-image hatasi:', error);
      figma.ui.postMessage({
        type: 'error',
        message: 'Gorsel alinamadi.'
      });
    }
  }
  
  // Gorsel uygulama istegi
  if (msg.type === 'apply-image') {
    const { imageBase64, nodeId, nodeName, width, height, isUpscaled } = msg.data;
    await applyImageToNode(imageBase64, nodeId, nodeName, width, height, isUpscaled);
  }

  // Icon ekleme istegi
  if (msg.type === 'insert-icon') {
    try {
      const data = msg.data || {};
      const svg = data.svg;
      const name = data.name || data.id || 'Icon';

      if (!svg || typeof svg !== 'string') {
        figma.ui.postMessage({
          type: 'error',
          message: 'Ikon verisi alinamadi.'
        });
        return;
      }

      // SVG'den node olustur
      const node = figma.createNodeFromSvg(svg);
      node.name = 'Icon / ' + name;

      // Sayfaya ekle ve viewport merkezine konumlandir
      figma.currentPage.appendChild(node);

      const viewport = figma.viewport;
      const center = viewport.center;

      node.x = center.x - node.width / 2;
      node.y = center.y - node.height / 2;

      figma.currentPage.selection = [node];
      figma.viewport.scrollAndZoomIntoView([node]);

      figma.ui.postMessage({
        type: 'success',
        message: 'Ikon Figma dokumanina eklendi.'
      });
    } catch (error) {
      var errorMessage = error && error.message ? error.message : String(error);
      figma.ui.postMessage({
        type: 'error',
        message: 'Ikon eklenemedi: ' + errorMessage
      });
      console.error('insert-icon error:', error);
    }
  }
};

// Plugin kapatildiginda
figma.on('close', () => {
  // Cleanup
});
