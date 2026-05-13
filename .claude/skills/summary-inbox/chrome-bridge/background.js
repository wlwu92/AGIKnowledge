// Summary Inbox Bridge — connects Native Messaging Host ↔ chrome.bookmarks API
const HOST_NAME = 'com.claude.summary_inbox';
let port = null;
let pendingRequests = new Map();
let requestId = 0;

function connect() {
  try {
    port = chrome.runtime.connectNative(HOST_NAME);
    port.onMessage.addListener(onHostMessage);
    port.onDisconnect.addListener(() => {
      console.error('Native host disconnected:', chrome.runtime.lastError?.message);
      port = null;
      // Reconnect after a delay
      setTimeout(connect, 3000);
    });
    console.log('Connected to native host');
  } catch (e) {
    console.error('Failed to connect to native host:', e);
    setTimeout(connect, 5000);
  }
}

async function onHostMessage(msg) {
  if (msg.event === 'ready') {
    console.log('Native host ready');
    return;
  }

  if (msg.cmd === 'moveBookmark') {
    try {
      const result = await moveBookmark(msg.url, msg.targetFolder);
      sendResponse(msg.id, { status: 'ok', ...result });
    } catch (e) {
      sendResponse(msg.id, { status: 'error', error: e.message });
    }
    return;
  }

  if (msg.cmd === 'listFolder') {
    try {
      const bookmarks = await listFolder(msg.name, msg.parent);
      sendResponse(msg.id, { status: 'ok', bookmarks });
    } catch (e) {
      sendResponse(msg.id, { status: 'error', error: e.message });
    }
    return;
  }

  if (msg.cmd === 'findFolder') {
    try {
      const id = await findFolderId(msg.name);
      sendResponse(msg.id, { status: 'ok', id });
    } catch (e) {
      sendResponse(msg.id, { status: 'error', error: e.message });
    }
    return;
  }

  if (msg.cmd === 'createFolder') {
    try {
      const folder = await createFolder(msg.name, msg.parentId);
      sendResponse(msg.id, { status: 'ok', id: folder.id });
    } catch (e) {
      sendResponse(msg.id, { status: 'error', error: e.message });
    }
    return;
  }
}

function sendResponse(id, data) {
  if (!port) return;
  try {
    port.postMessage({ responseTo: id, ...data });
  } catch (e) {
    console.error('Failed to send response:', e);
  }
}

// --- chrome.bookmarks API wrappers ---

async function findFolderId(name) {
  const tree = await chrome.bookmarks.getTree();
  return findFolderInTree(tree[0], name);
}

function findFolderInTree(node, name) {
  if (node.title === name && !node.url) return node.id;
  if (node.children) {
    for (const child of node.children) {
      const found = findFolderInTree(child, name);
      if (found) return found;
    }
  }
  return null;
}

async function createFolder(name, parentId) {
  return chrome.bookmarks.create({
    parentId,
    title: name,
    type: 'folder'
  });
}

async function listFolder(name, parentName) {
  const tree = await chrome.bookmarks.getTree();
  function walk(node) {
    const items = [];
    if (node.children) {
      for (const child of node.children) {
        if (child.url) {
          items.push({
            id: child.id,
            title: child.title,
            url: child.url,
            parentId: child.parentId
          });
        }
        if (child.children) {
          items.push(...walk(child));
        }
      }
    }
    return items;
  }
  return walk(tree[0]);
}

async function moveBookmark(url, targetFolderName) {
  // Search for the bookmark by URL
  const results = await chrome.bookmarks.search({ url });
  if (results.length === 0) {
    throw new Error(`Bookmark not found: ${url}`);
  }

  const bookmark = results[0];

  // Find target folder
  let targetId = await findFolderId(targetFolderName);
  if (!targetId) {
    // Create Archives folder under Other Bookmarks
    const other = (await chrome.bookmarks.getTree())[0].children
      .find(n => n.title === 'Other bookmarks' || n.id === '2');
    const folder = await chrome.bookmarks.create({
      parentId: other ? other.id : '2',
      title: targetFolderName
    });
    targetId = folder.id;
  }

  // Move the bookmark
  await chrome.bookmarks.move(bookmark.id, { parentId: targetId });
  return {
    title: bookmark.title,
    from: bookmark.parentId,
    to: targetId
  };
}

// Connect when service worker starts
connect();

// Keep alive: reconnect on failure
chrome.runtime.onStartup.addListener(connect);
