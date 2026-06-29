# Browser Extensions & Integration

Mediathread offers tools to integrate with your web browsing experience, allowing you to bring external content into your course environment easily.

## The "Save to Mediathread" Bookmarklet

The primary tool for external content is the **Mediathread Bookmarklet** (often referred to as the browser extension).

### Installation
1.  Log in to Mediathread.
2.  Look for the **"Tools"** or **"Bookmarklet"** link in the footer or your profile menu.
3.  Drag the **"Save to Mediathread"** button to your browser's Bookmarks Bar.

### Usage
1.  Browse to a supported site (e.g., Flickr, YouTube, or a library archive).
2.  When you see an image or video you want to analyze, click the **"Save to Mediathread"** bookmark in your bar.
3.  A popup will appear, analyzing the page for compatible metadata (Schema.org, etc.).
4.  Select the Course you want to save the asset to.
5.  Click **Save**. The asset is now available in your Mediathread Collection.

## Metadata Standards (Schema.org)
Mediathread relies on structured metadata to understand external pages. It specifically looks for **Schema.org** markup (using `itemscope`, `itemtype`, and `itemprop`).

*   **Why is this important?** It allows Mediathread to automatically pull in the Title, Author, License, and Source URL of the media.
*   **Extensions:** While we use the term "Extension" to describe this capability, it is technically a Javascript bookmarklet that acts as a bridge between the open web and your private course.

!!! note "MCP"
    You may have heard of other integration protocols. Mediathread focuses on **LTI** for LMS integration and **Schema.org/Bookmarklets** for content integration. It does not currently utilize the "Model Context Protocol" (MCP).
