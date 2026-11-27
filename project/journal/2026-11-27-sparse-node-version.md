# Keep the Node pin in sparse cook jobs

Stamp repo-kit a066ebb and its Node 26 pin for QA32. The two publish
workflows retain the pin in their sparse checkouts. The CI setup step
and both publish workflows read the same pin.
