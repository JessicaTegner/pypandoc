-- taken from: https://pandoc.org/lua-filters.html
function Strong(elem)
    return pandoc.SmallCaps(elem.c)
end
