# Try one research question with WIT

## On a phone or in your usual chat

Open the [public starter text](https://raw.githubusercontent.com/iJaspers/manager-os/a2789ef29a7a34b7709c01beb5d92600cb1f35c6/downloads/MOS_PUBLIC_PACK_v2026.10.12-R1.txt). Copy its text into your chat, or attach the file if your app supports it. Then paste this and replace the bracketed question.

> Use this WIT starter for this conversation. Help me investigate [your question]. Tell me whether you can search and where I can save the result. If you can search, check an authoritative source and put its link beside the finding. Otherwise ask me for a link or excerpt you can read. Separate what the source says from your inference. Flag anything still open and give me one next step.

Try “Why can I sometimes see the Moon during the day?” When you finish, ask for a short return note with your question, finding, source links, next action and open questions. Save the note somewhere you control. To continue in a fresh chat, paste the starter and the note and ask the chat to pick up the next action.

## On a computer with the downloaded ZIP

Download the [23 November 2026 public ZIP](https://raw.githubusercontent.com/iJaspers/manager-os/a2789ef29a7a34b7709c01beb5d92600cb1f35c6/tools/releases/discovery-scout-2026-11-23/WIT_Discovery_Scout_Public_2026-11-23.zip) and extract it. Open a terminal in the folder where you see both `Scout_Explain` and `WIT`. With Python 3 available, run:

```sh
python3 Scout_Explain/provider_adapter.py Scout_Explain/example_results.json --goal "community grant checklist" --level simple
```

The first result should be **Fictional community grant checklist**. The bundled example contains invented snippets. Scout ranks the text you supply and labels the limits of its evidence. Your chat or another search provider supplies the sources for a real inquiry.

To try your own results, copy the example JSON to a new file, replace its titles, URLs and excerpts with public sources for your question, and use that filename and question in the command. For a repository checkout, the [general-inquiry guide](releases/discovery-scout-2026-11-23/GENERAL_INQUIRIES.md) includes a separate multi-topic example and checkout-specific commands.
