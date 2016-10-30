<div id="mw-page-base" class="noprint">

</div>

<div id="mw-head-base" class="noprint">

</div>

<div id="content" class="mw-body" role="main">

[](){#top}
<div id="siteNotice">

</div>

<div class="mw-indicators">

</div>

file URI scheme {#firstHeading .firstHeading lang="en"}
===============

<div id="bodyContent" class="mw-body-content">

<div id="siteSub">

From Wikipedia, the free encyclopedia

</div>

<div id="contentSub">

</div>

<div id="jump-to-nav" class="mw-jump">

Jump to: [navigation](#mw-head), [search](#p-search)

</div>

<div id="mw-content-text" class="mw-content-ltr" lang="en" dir="ltr">

+--------------------------------------+--------------------------------------+
| <div style="width:52px">             | <span class="mbox-text-span">This    |
|                                      | article **needs additional citations |
| [![](//upload.wikimedia.org/wikipedi | for                                  |
| a/en/thumb/9/99/Question_book-new.sv | [verification](/wiki/Wikipedia:Verif |
| g/50px-Question_book-new.svg.png){wi | iability "Wikipedia:Verifiability")* |
| dth="50"                             | *.                                   |
| height="39"                          | <span                                |
| srcset="//upload.wikimedia.org/wikip | class="hide-when-compact">Please     |
| edia/en/thumb/9/99/Question_book-new | help [improve this                   |
| .svg/75px-Question_book-new.svg.png  | article](//en.wikipedia.org/w/index. |
| 1.5x, //upload.wikimedia.org/wikiped | php?title=File_URI_scheme&action=edi |
| ia/en/thumb/9/99/Question_book-new.s | t){.external                         |
| vg/100px-Question_book-new.svg.png 2 | .text} by [adding citations to       |
| x"}](/wiki/File:Question_book-new.sv | reliable                             |
| g){.image}                           | sources](/wiki/Help:Introduction_to_ |
|                                      | referencing_with_Wiki_Markup/1 "Help |
| </div>                               | :Introduction to referencing with Wi |
|                                      | ki Markup/1").                       |
|                                      | Unsourced material may be challenged |
|                                      | and removed.</span> *(October 2012)* |
|                                      | *([Learn how and when to remove this |
|                                      | template                             |
|                                      | message](/wiki/Help:Maintenance_temp |
|                                      | late_removal "Help:Maintenance templ |
|                                      | ate removal"))*</span>               |
+--------------------------------------+--------------------------------------+

The **file URI scheme** is a [URI
scheme](/wiki/URI_scheme "URI scheme"){.mw-redirect} specified in [RFC
1630](//tools.ietf.org/html/rfc1630){.external .mw-magiclink-rfc} and
[RFC 1738](//tools.ietf.org/html/rfc1738){.external .mw-magiclink-rfc},
typically used to retrieve files from within one's own computer. The
[Internet Engineering Task
Force](/wiki/Internet_Engineering_Task_Force "Internet Engineering Task Force")
(IETF) has published a series of [draft
documents](/wiki/Draft_document "Draft document") obsoleting these RFCs.
They say that they are trying to define "a syntax that is compatible
with most extant implementations, while attempting to push towards a
stricter subset of 'ideal' constructs." Doing so involves the
[deprecation](/wiki/Deprecation "Deprecation") of some less common or
outdated constructs, some of which are described below. While they may
work on some current systems, formulations that are not consistent with
the [standardization](/wiki/Standardization "Standardization") process
going forward will not have the useful lifetime that others will. The
drafts are not final, and should be consulted for up to date
information.^[\[1\]](#cite_note-1)^

<div id="toc" class="toc">

<div id="toctitle">

Contents
--------

</div>

-   [<span class="tocnumber">1</span> <span
    class="toctext">Format</span>](#Format)
-   [<span class="tocnumber">2</span> <span class="toctext">Meaning of
    slash character</span>](#Meaning_of_slash_character)
-   [<span class="tocnumber">3</span> <span
    class="toctext">Examples</span>](#Examples)
    -   [<span class="tocnumber">3.1</span> <span
        class="toctext">Unix</span>](#Unix)
    -   [<span class="tocnumber">3.2</span> <span
        class="toctext">Windows</span>](#Windows)
-   [<span class="tocnumber">4</span> <span
    class="toctext">Implementations</span>](#Implementations)
    -   [<span class="tocnumber">4.1</span> <span
        class="toctext">Windows</span>](#Windows_2)
        -   [<span class="tocnumber">4.1.1</span> <span
            class="toctext">Legacy URLs</span>](#Legacy_URLs)
    -   [<span class="tocnumber">4.2</span> <span class="toctext">Web
        pages</span>](#Web_pages)
-   [<span class="tocnumber">5</span> <span
    class="toctext">References</span>](#References)
-   [<span class="tocnumber">6</span> <span class="toctext">External
    links</span>](#External_links)

</div>

<span id="Format" class="mw-headline">Format</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=1 "Edit section: Format")<span class="mw-editsection-bracket">\]</span></span>
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

A file URI takes the form of

    file://host/path

where ***host*** is the [fully qualified domain
name](/wiki/Fully_qualified_domain_name "Fully qualified domain name")
of the system on which the *path* is accessible, and ***path*** is a
hierarchical directory path of the form
*directory*/*directory*/.../*name*. If *host* is omitted, it is taken to
be "[localhost](/wiki/Localhost "Localhost")", the machine from which
the URL is being interpreted. Note that when omitting host, the slash is
not omitted (while "file:///foo.txt" is valid, "file://foo.txt" is not,
although some interpreters manage to handle the latter).

\[[RFC 3986](//tools.ietf.org/html/rfc3986){.external
.mw-magiclink-rfc}\] includes additional information about the treatment
of ".." and "." segments in URIs.

<span id="Meaning_of_slash_character" class="mw-headline">Meaning of slash character</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=2 "Edit section: Meaning of slash character")<span class="mw-editsection-bracket">\]</span></span>
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

The **slash character** (/), depending on its position, has different
meanings within a file URL.

-   The // after the *file:* is part of the general syntax of
    [URLs](/wiki/Uniform_resource_locator "Uniform resource locator"){.mw-redirect}.
    (The double slash // should always appear in a file URL according to
    the specification, but in practice many [Web
    browsers](/wiki/Web_browser "Web browser") allow it to be omitted).
-   The single slash between ***host*** and ***path*** is part of the
    syntax of URLs.
-   The slashes in ***path*** separate directory names in a hierarchical
    system of directories and subdirectories. In this usage, the slash
    is a general, system-independent way of separating the parts, and in
    a particular host system it might be used as such in any pathname
    (as in Unix systems).

<span id="Examples" class="mw-headline">Examples</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=3 "Edit section: Examples")<span class="mw-editsection-bracket">\]</span></span>
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### <span id="Unix" class="mw-headline">Unix</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=4 "Edit section: Unix")<span class="mw-editsection-bracket">\]</span></span>

Here are two [Unix](/wiki/Unix "Unix") examples pointing to the same
/*etc*/*fstab* file:

    file://localhost/etc/fstab
    file:///etc/fstab

### <span id="Windows" class="mw-headline">Windows</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=5 "Edit section: Windows")<span class="mw-editsection-bracket">\]</span></span>

Here are some examples which may be accepted by some applications on
Windows systems, referring to the same, local file
*c:*\\*WINDOWS*\\*clock.avi*

    file://localhost/c|/WINDOWS/clock.avi
    file:///c|/WINDOWS/clock.avi
    file://localhost/c:/WINDOWS/clock.avi

Here is the URI as understood by the Windows Shell
API:^[\[2\]](#cite_note-2)^

    file:///c:/WINDOWS/clock.avi

<span id="Implementations" class="mw-headline">Implementations</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=6 "Edit section: Implementations")<span class="mw-editsection-bracket">\]</span></span>
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### <span id="Windows_2" class="mw-headline">Windows</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=7 "Edit section: Windows")<span class="mw-editsection-bracket">\]</span></span>

On Microsoft Windows systems, the normal colon (:) after a device letter
has sometimes been replaced by a vertical bar (|) in file URLs. This
reflected the original URL syntax, which made the colon a reserved
character in a path part.

Since [Internet Explorer
4](/wiki/Internet_Explorer_4 "Internet Explorer 4"), file URIs have been
standardized on Windows, and should follow the following scheme. This
applies to all applications which use URLMON or SHLWAPI for parsing,
fetching or binding to URIs. To convert a path to a URL, use
`UrlCreateFromPath`, and to convert a URL to a path, use
`PathCreateFromUrl`.^[\[3\]](#cite_note-3)^

To access a file "the file.txt", the following might be used.

For a network location:

    file://hostname/path/to/the%20file.txt

Or for a local file, the hostname is omitted, but the slash is not (note
the third slash):

    file:///c:/path/to/the%20file.txt

This is not the same as providing the string "localhost" or the dot "."
in place of the hostname. The string "localhost" will attempt to access
the file as \\\\localhost\\c:\\path\\to\\the file.txt, which will not
work since the colon is not allowed in a share name. The dot "." results
in the string being passed as \\\\.\\c:\\path\\to\\the file.txt, which
will work for local files, but not shares on the local system. For
example file://./sharename/path/to/the%20file.txt will not work, because
it will result in *sharename* being interpreted as part of the
DOSDEVICES namespace, not as a network share.

The following outline roughly describes the requirements.

-   The colon should be used, and should *not* be replaced with a
    vertical bar for Internet Explorer.
-   Forward slashes should be used to delimit paths.
-   Characters such as the hash (\#) or question mark (?) which are part
    of the filename should be
    [percent-encoded](/wiki/Percent-encoding "Percent-encoding").
-   Characters which are not allowed in URIs, but which are allowed in
    filenames, must also be percent-encoded. For example, any of
    "**{}\`\^** " and all control characters. In the example above, the
    space in the filename is encoded as %20.
-   Characters which are allowed in both URIs and filenames must NOT
    be percent-encoded.
-   Must not use legacy ACP encodings. (ACP code pages are specified by
    DOS CHCP or Windows Control Panel language setting.)
-   Unicode characters outside of the [ASCII](/wiki/ASCII "ASCII") range
    must be [UTF-8](/wiki/UTF-8 "UTF-8") encoded, and those UTF-8
    encodings must be percent-encoded.

Use the provided functions if possible. If must create a URL
programmatically and cannot access SHLWAPI.dll (for example from script,
or another programming environment where the equivalent functions are
not available) the above outline will help.

#### <span id="Legacy_URLs" class="mw-headline">Legacy URLs</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=8 "Edit section: Legacy URLs")<span class="mw-editsection-bracket">\]</span></span>

To aid the installed base of legacy applications on Win32
`PathCreateFromUrl` recognizes certain URLs which do not meet these
criteria, and treats them uniformly. These are called "legacy" file URLs
as opposed to "healthy" file URLs.^[\[4\]](#cite_note-4)^

In the past, a variety of other applications have used other systems.
Some added an additional two slashes. For example,
\\\\remotehost\\share\\dir\\file.txt, would become
file:////remotehost/share/dir/file.txt instead of the "healthy"
file://remotehost/share/dir/file.txt.

### <span id="Web_pages" class="mw-headline">Web pages</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=9 "Edit section: Web pages")<span class="mw-editsection-bracket">\]</span></span>

File URLs are rarely used in [Web pages](/wiki/Web_page "Web page") on
the public Internet, since they imply that a file exists on the
designated host. The *host* specifier can be used to retrieve a file
from an external source, although no specific file-retrieval protocol is
specified; and using it should result in a message that informs the user
that no mechanism to access that machine is available.

<span id="References" class="mw-headline">References</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=10 "Edit section: References")<span class="mw-editsection-bracket">\]</span></span>
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

<div class="reflist" style="list-style-type: decimal;">

1.  <div id="cite_note-1">

    </div>

    <span class="mw-cite-backlink">**[\^](#cite_ref-1)**</span> <span
    class="reference-text">["The file URI Scheme:
    draft-ietf-appsawg-file-scheme-03"](https://tools.ietf.org/html/draft-ietf-appsawg-file-scheme-03){.external
    .text}. Internet Engineering Task Force (IETF). 23 July 2015<span
    class="reference-accessdate">. Retrieved <span class="nowrap">21
    Aug</span> 2015</span>.<span class="Z3988"
    title="ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fen.wikipedia.org%3AFile+URI+scheme&amp;rft.btitle=The+file+URI+Scheme%3A+draft-ietf-appsawg-file-scheme-03&amp;rft.date=2015-07-23&amp;rft.genre=unknown&amp;rft_id=https%3A%2F%2Ftools.ietf.org%2Fhtml%2Fdraft-ietf-appsawg-file-scheme-03&amp;rft.pub=Internet+Engineering+Task+Force+%28IETF%29&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Abook"><span
    style="display:none;"> </span></span></span>
2.  <div id="cite_note-2">

    </div>

    <span class="mw-cite-backlink">**[\^](#cite_ref-2)**</span> <span
    class="reference-text">Risney, Dave (2006). ["File URIs in
    Windows"](http://blogs.msdn.com/b/ie/archive/2006/12/06/file-uris-in-windows.aspx){.external
    .text}. *IEBlog*. Microsoft Corporation<span
    class="reference-accessdate">. Retrieved <span class="nowrap">31
    July</span> 2013</span>.<span class="Z3988"
    title="ctx_ver=Z39.88-2004&amp;rfr_id=info%3Asid%2Fen.wikipedia.org%3AFile+URI+scheme&amp;rft.atitle=File+URIs+in+Windows&amp;rft.aufirst=Dave&amp;rft.aulast=Risney&amp;rft.date=2006&amp;rft.genre=unknown&amp;rft_id=http%3A%2F%2Fblogs.msdn.com%2Fb%2Fie%2Farchive%2F2006%2F12%2F06%2Ffile-uris-in-windows.aspx&amp;rft.jtitle=IEBlog&amp;rft_val_fmt=info%3Aofi%2Ffmt%3Akev%3Amtx%3Ajournal"><span
    style="display:none;"> </span></span></span>
3.  <div id="cite_note-3">

    </div>

    <span class="mw-cite-backlink">**[\^](#cite_ref-3)**</span> <span
    class="reference-text">[File URIs in Windows - IEBlog - Site Home -
    MSDN
    Blogs](http://blogs.msdn.com/ie/archive/2006/12/06/file-uris-in-windows.aspx){.external
    .text}. Blogs.msdn.com (2006-12-06). Retrieved on 2014-03-08.</span>
4.  <div id="cite_note-4">

    </div>

    <span class="mw-cite-backlink">**[\^](#cite_ref-4)**</span> <span
    class="reference-text">[The Bizarre and Unhappy Story of 'file:'
    URLs - Free Associations - Site Home - MSDN
    Blogs](http://blogs.msdn.com/freeassociations/archive/2005/05/19/420059.aspx){.external
    .text}. Blogs.msdn.com (2005-05-19). Retrieved on 2014-03-08.</span>

</div>

<span id="External_links" class="mw-headline">External links</span><span class="mw-editsection"><span class="mw-editsection-bracket">\[</span>[edit](/w/index.php?title=File_URI_scheme&action=edit&section=11 "Edit section: External links")<span class="mw-editsection-bracket">\]</span></span>
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-   [File URLs](http://www.cs.tut.fi/~jkorpela/fileurl.html){.external
    .text}

<div class="navbox" role="navigation"
aria-labelledby="Uniform_Resource_Identifier_.28URI.29_schemes"
style="padding:3px">

<div class="plainlinks hlist navbar mini">

-   [v](/wiki/Template:URI_schemes "Template:URI schemes")
-   [t](/wiki/Template_talk:URI_schemes "Template talk:URI schemes")
-   [e](//en.wikipedia.org/w/index.php?title=Template:URI_schemes&action=edit){.external
    .text}

</div>

<div id="Uniform_Resource_Identifier_.28URI.29_schemes"
style="font-size:114%">

[Uniform Resource
Identifier](/wiki/Uniform_Resource_Identifier "Uniform Resource Identifier")
(URI) schemes

</div>

Official
<div style="padding:0em 0.25em">

-   [about](/wiki/About_URI_scheme "About URI scheme")
-   [acct](/wiki/Acct_(protocol) "Acct (protocol)")
-   [crid](/wiki/Content_reference_identifier "Content reference identifier")
-   [data](/wiki/Data_URI_scheme "Data URI scheme")
-   **file**
-   [geo](/wiki/Geo_URI_scheme "Geo URI scheme")
-   [http](/wiki/Hypertext_Transfer_Protocol#Technical_overview "Hypertext Transfer Protocol")
-   [https](/wiki/HTTPS#Overview "HTTPS")
-   [info](/wiki/Info_URI_scheme "Info URI scheme")
-   [ldap](/wiki/Lightweight_Directory_Access_Protocol#URI_scheme "Lightweight Directory Access Protocol")
-   [mailto](/wiki/Mailto "Mailto")
-   [sip / sips](/wiki/SIP_URI_scheme "SIP URI scheme")
-   [tag](/wiki/Tag_URI "Tag URI"){.mw-redirect}
-   [urn](/wiki/Uniform_resource_name "Uniform resource name"){.mw-redirect}
-   [view-source](/wiki/View-source_URI_scheme "View-source URI scheme")
-   [ws / wss](/wiki/WebSocket#Overview "WebSocket")

</div>

Unofficial
<div style="padding:0em 0.25em">

-   [coffee](/wiki/Hyper_Text_Coffee_Pot_Control_Protocol#Commands_and_replies "Hyper Text Coffee Pot Control Protocol")
-   [ed2k](/wiki/Ed2k_URI_scheme "Ed2k URI scheme")
-   [feed](/wiki/Feed_URI_scheme "Feed URI scheme")
-   [irc / irc6 /
    ircs](/wiki/Internet_Relay_Chat#URI_scheme "Internet Relay Chat")
-   [ldaps](/wiki/Lightweight_Directory_Access_Protocol#URI_scheme "Lightweight Directory Access Protocol")
-   [magnet](/wiki/Magnet_URI_scheme "Magnet URI scheme")
-   [ymsgr](/wiki/Yahoo!_Messenger#URI_scheme "Yahoo! Messenger")

</div>

<div>

[Protocol
list](/wiki/List_of_network_protocols_(OSI_model) "List of network protocols (OSI model)")

</div>

</div>

![](//en.wikipedia.org/wiki/Special:CentralAutoLogin/start?type=1x1){width="1"
height="1"}

</div>

<div class="printfooter">

Retrieved from
"<https://en.wikipedia.org/w/index.php?title=File_URI_scheme&oldid=723314037>"

</div>

<div id="catlinks" class="catlinks" data-mw="interface">

<div id="mw-normal-catlinks" class="mw-normal-catlinks">

[Categories](/wiki/Help:Category "Help:Category"):
-   [Internet
    Standards](/wiki/Category:Internet_Standards "Category:Internet Standards")
-   [Identifiers](/wiki/Category:Identifiers "Category:Identifiers")
-   [URI schemes](/wiki/Category:URI_schemes "Category:URI schemes")

</div>

<div id="mw-hidden-catlinks"
class="mw-hidden-catlinks mw-hidden-cats-hidden">

Hidden categories:
-   [Articles needing additional references from October
    2012](/wiki/Category:Articles_needing_additional_references_from_October_2012 "Category:Articles needing additional references from October 2012")
-   [All articles needing additional
    references](/wiki/Category:All_articles_needing_additional_references "Category:All articles needing additional references")

</div>

</div>

<div class="visualClear">

</div>

</div>

</div>

<div id="mw-navigation">

Navigation menu
---------------

<div id="mw-head">

<div id="p-personal" role="navigation"
aria-labelledby="p-personal-label">

### Personal tools {#p-personal-label}

-   <div id="pt-anonuserpage">

    </div>

    Not logged in
-   <div id="pt-anontalk">

    </div>

    [Talk](/wiki/Special:MyTalk "Discussion about edits from this IP address [n]")
-   <div id="pt-anoncontribs">

    </div>

    [Contributions](/wiki/Special:MyContributions "A list of edits made from this IP address [y]")
-   <div id="pt-createaccount">

    </div>

    [Create
    account](/w/index.php?title=Special:CreateAccount&returnto=File+URI+scheme "You are encouraged to create an account and log in; however, it is not mandatory")
-   <div id="pt-login">

    </div>

    [Log
    in](/w/index.php?title=Special:UserLogin&returnto=File+URI+scheme "You're encouraged to log in; however, it's not mandatory. [o]")

</div>

<div id="left-navigation">

<div id="p-namespaces" class="vectorTabs" role="navigation"
aria-labelledby="p-namespaces-label">

### Namespaces {#p-namespaces-label}

-   <div id="ca-nstab-main">

    </div>

    <span>[Article](/wiki/File_URI_scheme "View the content page [c]")</span>
-   <div id="ca-talk">

    </div>

    <span>[Talk](/wiki/Talk:File_URI_scheme "Discussion about the content page [t]")</span>

</div>

<div id="p-variants" class="vectorMenu emptyPortlet" role="navigation"
aria-labelledby="p-variants-label">

### <span>Variants</span>[](#) {#p-variants-label}

<div class="menu">

</div>

</div>

</div>

<div id="right-navigation">

<div id="p-views" class="vectorTabs" role="navigation"
aria-labelledby="p-views-label">

### Views {#p-views-label}

-   <div id="ca-view">

    </div>

    <span>[Read](/wiki/File_URI_scheme)</span>
-   <div id="ca-edit">

    </div>

    <span>[Edit](/w/index.php?title=File_URI_scheme&action=edit "Edit this page [e]")</span>
-   <div id="ca-history">

    </div>

    <span>[View
    history](/w/index.php?title=File_URI_scheme&action=history "Past revisions of this page [h]")</span>

</div>

<div id="p-cactions" class="vectorMenu emptyPortlet" role="navigation"
aria-labelledby="p-cactions-label">

### <span>More</span>[](#) {#p-cactions-label}

<div class="menu">

</div>

</div>

<div id="p-search" role="search">

### Search

<div id="simpleSearch">

</div>

</div>

</div>

</div>

<div id="mw-panel">

<div id="p-logo" role="banner">

[](/wiki/Main_Page "Visit the main page"){.mw-wiki-logo}

</div>

<div id="p-navigation" class="portal" role="navigation"
aria-labelledby="p-navigation-label">

### Navigation {#p-navigation-label}

<div class="body">

-   <div id="n-mainpage-description">

    </div>

    [Main page](/wiki/Main_Page "Visit the main page [z]")
-   <div id="n-contents">

    </div>

    [Contents](/wiki/Portal:Contents "Guides to browsing Wikipedia")
-   <div id="n-featuredcontent">

    </div>

    [Featured
    content](/wiki/Portal:Featured_content "Featured content – the best of Wikipedia")
-   <div id="n-currentevents">

    </div>

    [Current
    events](/wiki/Portal:Current_events "Find background information on current events")
-   <div id="n-randompage">

    </div>

    [Random article](/wiki/Special:Random "Load a random article [x]")
-   <div id="n-sitesupport">

    </div>

    [Donate to
    Wikipedia](https://donate.wikimedia.org/wiki/Special:FundraiserRedirector?utm_source=donate&utm_medium=sidebar&utm_campaign=C13_en.wikipedia.org&uselang=en "Support us")
-   <div id="n-shoplink">

    </div>

    [Wikipedia store](//shop.wikimedia.org "Visit the Wikipedia store")

</div>

</div>

<div id="p-interaction" class="portal" role="navigation"
aria-labelledby="p-interaction-label">

### Interaction {#p-interaction-label}

<div class="body">

-   <div id="n-help">

    </div>

    [Help](/wiki/Help:Contents "Guidance on how to use and edit Wikipedia")
-   <div id="n-aboutsite">

    </div>

    [About Wikipedia](/wiki/Wikipedia:About "Find out about Wikipedia")
-   <div id="n-portal">

    </div>

    [Community
    portal](/wiki/Wikipedia:Community_portal "About the project, what you can do, where to find things")
-   <div id="n-recentchanges">

    </div>

    [Recent
    changes](/wiki/Special:RecentChanges "A list of recent changes in the wiki [r]")
-   <div id="n-contactpage">

    </div>

    [Contact
    page](//en.wikipedia.org/wiki/Wikipedia:Contact_us "How to contact Wikipedia")

</div>

</div>

<div id="p-tb" class="portal" role="navigation"
aria-labelledby="p-tb-label">

### Tools {#p-tb-label}

<div class="body">

-   <div id="t-whatlinkshere">

    </div>

    [What links
    here](/wiki/Special:WhatLinksHere/File_URI_scheme "List of all English Wikipedia pages containing links to this page [j]")
-   <div id="t-recentchangeslinked">

    </div>

    [Related
    changes](/wiki/Special:RecentChangesLinked/File_URI_scheme "Recent changes in pages linked from this page [k]")
-   <div id="t-upload">

    </div>

    [Upload file](/wiki/Wikipedia:File_Upload_Wizard "Upload files [u]")
-   <div id="t-specialpages">

    </div>

    [Special
    pages](/wiki/Special:SpecialPages "A list of all special pages [q]")
-   <div id="t-permalink">

    </div>

    [Permanent
    link](/w/index.php?title=File_URI_scheme&oldid=723314037 "Permanent link to this revision of the page")
-   <div id="t-info">

    </div>

    [Page
    information](/w/index.php?title=File_URI_scheme&action=info "More information about this page")
-   <div id="t-wikibase">

    </div>

    [Wikidata
    item](https://www.wikidata.org/wiki/Q5448333 "Link to connected data repository item [g]")
-   <div id="t-cite">

    </div>

    [Cite this
    page](/w/index.php?title=Special:CiteThisPage&page=File_URI_scheme&id=723314037 "Information on how to cite this page")

</div>

</div>

<div id="p-coll-print_export" class="portal" role="navigation"
aria-labelledby="p-coll-print_export-label">

### Print/export {#p-coll-print_export-label}

<div class="body">

-   <div id="coll-create_a_book">

    </div>

    [Create a
    book](/w/index.php?title=Special:Book&bookcmd=book_creator&referer=File+URI+scheme)
-   <div id="coll-download-as-rdf2latex">

    </div>

    [Download as
    PDF](/w/index.php?title=Special:Book&bookcmd=render_article&arttitle=File+URI+scheme&returnto=File+URI+scheme&oldid=723314037&writer=rdf2latex)
-   <div id="t-print">

    </div>

    [Printable
    version](/w/index.php?title=File_URI_scheme&printable=yes "Printable version of this page [p]")

</div>

</div>

<div id="p-lang" class="portal" role="navigation"
aria-labelledby="p-lang-label">

### Languages {#p-lang-label}

<div class="body">

-   [Français](https://fr.wikipedia.org/wiki/File_URI_scheme "File URI scheme – French"){.interlanguage-link-target}
-   [Русский](https://ru.wikipedia.org/wiki/File_(%D1%81%D1%85%D0%B5%D0%BC%D0%B0_URI) "File (схема URI) – Russian"){.interlanguage-link-target}
-   [](#)

<div class="after-portlet after-portlet-lang">

<span class="wb-langlinks-edit wb-langlinks-link">[Edit
links](https://www.wikidata.org/wiki/Q5448333#sitelinks-wikipedia "Edit interlanguage links"){.wbc-editpage}</span>

</div>

</div>

</div>

</div>

</div>

<div id="footer" role="contentinfo">

-   <div id="footer-info-lastmod">

    </div>

    This page was last modified on 2 June 2016, at 09:21.
-   <div id="footer-info-copyright">

    </div>

    Text is available under the [Creative Commons Attribution-ShareAlike
    License](//en.wikipedia.org/wiki/Wikipedia:Text_of_Creative_Commons_Attribution-ShareAlike_3.0_Unported_License)[](//creativecommons.org/licenses/by-sa/3.0/);
    additional terms may apply. By using this site, you agree to the
    [Terms of Use](//wikimediafoundation.org/wiki/Terms_of_Use) and
    [Privacy Policy](//wikimediafoundation.org/wiki/Privacy_policy).
    Wikipedia® is a registered trademark of the [Wikimedia
    Foundation, Inc.](//www.wikimediafoundation.org/), a
    non-profit organization.

<!-- -->

-   <div id="footer-places-privacy">

    </div>

    [Privacy
    policy](https://wikimediafoundation.org/wiki/Privacy_policy "wmf:Privacy policy"){.extiw}
-   <div id="footer-places-about">

    </div>

    [About Wikipedia](/wiki/Wikipedia:About "Wikipedia:About")
-   <div id="footer-places-disclaimer">

    </div>

    [Disclaimers](/wiki/Wikipedia:General_disclaimer "Wikipedia:General disclaimer")
-   <div id="footer-places-contact">

    </div>

    [Contact Wikipedia](//en.wikipedia.org/wiki/Wikipedia:Contact_us)
-   <div id="footer-places-developers">

    </div>

    [Developers](https://www.mediawiki.org/wiki/Special:MyLanguage/How_to_contribute)
-   <div id="footer-places-cookiestatement">

    </div>

    [Cookie
    statement](https://wikimediafoundation.org/wiki/Cookie_statement)
-   <div id="footer-places-mobileview">

    </div>

    [Mobile
    view](//en.m.wikipedia.org/w/index.php?title=File_URI_scheme&mobileaction=toggle_view_mobile){.noprint
    .stopMobileRedirectToggle}

<!-- -->

-   <div id="footer-copyrightico">

    </div>

    [![Wikimedia
    Foundation](/static/images/wikimedia-button.png){width="88"
    height="31"
    srcset="/static/images/wikimedia-button-1.5x.png 1.5x, /static/images/wikimedia-button-2x.png 2x"}](https://wikimediafoundation.org/)
-   <div id="footer-poweredbyico">

    </div>

    [![Powered by
    MediaWiki](/static/images/poweredby_mediawiki_88x31.png){width="88"
    height="31"
    srcset="/static/images/poweredby_mediawiki_132x47.png 1.5x, /static/images/poweredby_mediawiki_176x62.png 2x"}](//www.mediawiki.org/)

<div style="clear:both">

</div>

</div>
