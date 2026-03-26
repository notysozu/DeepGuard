import { createServer } from 'vite';

async function run() {
  const vite = await createServer({
    server: { middlewareMode: true },
    appType: 'custom'
  });
  
  try {
    const { default: App } = await vite.ssrLoadModule('/src/App.jsx');
    const { renderToString } = await vite.ssrLoadModule('react-dom/server');
    const React = await vite.ssrLoadModule('react');
    
    console.log("Rendering App...");
    const html = renderToString(React.createElement(App));
    console.log("SUCCESS length:", html.length);
  } catch (e) {
    console.error("APP CRASH EXACT ERROR:");
    console.error(e);
  } finally {
    await vite.close();
  }
}

run();
