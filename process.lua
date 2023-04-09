function Math(elem)
  -- Preserve both inline and display math in dollar signs
  if elem.mathtype == "InlineMath" then
    return pandoc.RawInline("plain", "$" .. elem.text .. "$")
  elseif elem.mathtype == "DisplayMath" then
    return pandoc.RawInline("plain", "$$" .. elem.text .. "$$")
  end
end

function Image () return {} end
function Table () return {} end
function Figure () return {} end
