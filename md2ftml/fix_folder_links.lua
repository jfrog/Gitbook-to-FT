function Link(el)
    if not el.target:match("%.%w+$") then
        -- If the target does not have an extension, append "/README.md"
        el.target = el.target .. "/README.md"
        -- print("linked changed!")
    end
    return el
end

function escape_html(text)
  -- Replace special HTML characters with their corresponding entities
  text = text:gsub("&", "&amp;")
  text = text:gsub("<", "&lt;")
  text = text:gsub(">", "&gt;")
  text = text:gsub('"', "&quot;")
  text = text:gsub("'", "&#39;")
  return text
end


function CodeBlock(elem)
  -- Print the content of the code block to the console
  -- print("Code Block Content:\n" .. elem.text)

  -- Modify the outer <pre> tag by adding the class "programlisting"
  -- Note: We are using the `pandoc.RawBlock` to return the modified <pre> tag with the class
  local pre_tag = '<pre class="programlisting">' .. escape_html(elem.text) .. '</pre>'

  -- Return the modified block
  return pandoc.RawBlock('html', pre_tag)
end

local first_block_removed = false

function Pandoc(doc)
  -- Check if the first block has been removed
  if not first_block_removed then
    -- Remove the first block in the document
    table.remove(doc.blocks, 1)
    first_block_removed = true
  end
  return doc
end

local in_hint = false
local hint_type = ""
local collected_content = {}

function Para(elem)
  local text = pandoc.utils.stringify(elem)

  -- Check if it's the start of a hint block
  local start_hint_type = text:match("{%% hint style=\"(%w+)\" %%}")
  local end_hint = text:match("{%% endhint %%}")

  -- Mapping hint types to Fluid Topics classes
  local hint_classes = {
    success = "note",
    info = "tip",
    danger = "important",
    warning = "warning"
  }

  -- If it's the start of a hint block, initialize collection
  if start_hint_type and hint_classes[start_hint_type] then
    in_hint = true
    hint_type = start_hint_type
    collected_content = {} -- Reset collected content
    text = text:gsub("{%% hint style=\"(%w+)\" %%}", ""):match("^%s*(.-)%s*$") -- Remove hint tag
  end

  -- If inside a hint, collect the paragraph content
  if in_hint then
    table.insert(collected_content, text)

    -- If it's the end of the hint block, generate the final HTML
    if end_hint then
      in_hint = false
      text = text:gsub("{%% endhint %%}", ""):match("^%s*(.-)%s*$") -- Remove endhint tag
      collected_content[#collected_content] = text -- Update last paragraph

      local final_html = '<div class="' .. hint_classes[hint_type] .. '">\n'
      final_html = final_html .. '<h3 class="title">' .. hint_type:gsub("^%l", string.upper) .. '</h3>\n'
      final_html = final_html .. '<p>' .. table.concat(collected_content, "</p>\n<p>") .. '</p>\n'
      final_html = final_html .. '</div>\n'

      return pandoc.RawBlock("html", final_html)
    else
      return {} -- Remove intermediate paragraphs
    end
  end

  -- If it's not inside a hint block, return it as normal
  return elem
end

function Link(el)
  -- Print the URL for debugging
  --print("Processing link:", el.target)

  -- If the link starts with "http", leave it unchanged
  --if el.target:match("^https?://") then
    --print("  -> Absolute URL (unchanged):", el.target)
    --return el
  --end

  -- Otherwise, modify as needed (or leave it as-is)
  --print("  -> Relative URL (may be modified):", el.target)
  return el
end
