# 8-Minute English Presentation Script

## Slide 1: Title

Hello everyone.

I am Quanwei Tang from Soochow University.

Today I will present our work, **"Don't Just Listen, Try Planning"**, a graph-based retrieval-generation agent for long-form audio meeting understanding.

The core idea of this work is simple: when answering questions over long meeting audio, a model should not only listen to the whole recording passively. It should actively plan what evidence to search for, where to look, and how to verify the answer.

## Slide 2: Motivation

Let me start with the motivation.

Long-form audio meeting QA has two key challenges.

The first one is **Acoustic Missing**.
Many Speech LLMs transform audio into text-like tokens or rely heavily on ASR transcripts. This is effective for semantic content, but it loses paralinguistic information, such as emotion, prosody, loudness, and tone.

For example, if the question asks about a "sudden loud voice at the 19-minute mark," a text-only representation may know what was said, but it cannot reliably know how it was said.

The second challenge is **Context Fragmentation**.
Meetings are often longer than 30 minutes, and important evidence may be far apart. Standard RAG treats the transcript as flat text chunks, so it can miss multi-hop evidence across distant timestamps.

Our solution is **GRGA**, which reasons over a multi-dimensional graph, and **LongAudioQA**, a benchmark designed to evaluate both textual understanding and acoustic grounding.

## Slide 3: LongAudioQA

To study this problem, we construct **LongAudioQA**, a benchmark for long-form audio meeting question answering.

It contains three sub-corpora: AliMeeting, AMI Meeting, and DailyTalk. Together, they cover more than 54 hours of audio and over 16 thousand question-answer pairs.

We design five question types: factual, inferential, temporal, summarization, and acoustic-aware questions.

The most important category is **Acoustic-Aware QA**. These questions require the model to connect textual semantics with acoustic signals. For example, the model may need to identify who sounded angry, who raised their voice, or how the speaker's tone changed during the meeting.

For quality control, we use a hybrid LLM and human annotation process. The inter-annotator agreement is high, and timestamp alignment is also carefully checked.

So LongAudioQA is not only a QA dataset, but also a diagnostic benchmark for long audio reasoning.

## Slide 4: GRGA Architecture

Now I will introduce our method, **GRGA**.

The first component is a **multi-dimensional meeting graph**.

Each node represents an utterance, containing text, speaker information, timestamp, and the corresponding audio segment.

We then build several types of edges. Temporal edges connect adjacent turns. Reply edges capture short-time interactions between speakers. Speaker edges connect utterances from the same speaker. Entity and semantic edges capture shared keywords and coreference relations.

This graph structure allows the model to move beyond flat transcript retrieval.

The second component is the agent formulation. We model the reasoning process as a POMDP. The agent maintains a belief state, chooses actions from graph tools, observes retrieved evidence, and updates its reasoning history.

In practice, this gives the model a structured way to decide what to search, which speaker or time range to inspect, and when the evidence is enough.

## Slide 5: GRGA Planning

This slide shows the planning loop of GRGA.

The process follows a **Search-Reason-Verify** pattern.

First, the query is decomposed into useful constraints, such as entities, concepts, time expressions, and metadata.

Second, the planner generates an execution plan. Instead of retrieving once, it decides which tool should be used next.

Third, the tool executor searches the graph. The action space includes semantic search, temporal filtering, graph traversal, and audio access.

Then, the synthesizer generates an answer with supporting citations.

Finally, the self-reflector checks whether the answer is sufficiently grounded. If the verification score is low, the agent re-plans and searches again.

This loop is training-free. It relies on in-context learning, but the key difference from standard RAG is that retrieval is no longer one-shot. It becomes adaptive and evidence-driven.

## Slide 6: Experimental Results

Here are the main experimental results.

We compare GRGA with strong Speech LLM baselines, including Qwen3-Omni and MiMo-Audio, and RAG baselines, including text-based BGE-M3 and audio-based CLASP.

Across both AliMeeting and AMI Meeting, GRGA achieves the best performance in almost all question types.

The gains are especially clear on difficult categories.

On AMI inferential questions, GRGA reaches **65.3%**, while Text RAG only achieves **24.6%**. This shows that vector similarity alone is not enough for multi-hop meeting reasoning.

On acoustic-aware questions, GRGA also improves substantially. On AliMeeting, it reaches **39.9%**, compared with **18.5%** for the next-best baseline.

These results suggest that both graph structure and direct audio access are important for long-form audio QA.

## Slide 7: Analysis

We further conduct human evaluation and ablation studies.

In human evaluation, annotators judge the generated answers from several aspects, including correctness, coherence, and groundedness. GRGA consistently improves over the baseline, especially in groundedness. This means the answers are better supported by real meeting evidence rather than hallucinated content.

The ablation study also shows that each module contributes to performance.

Removing reflection causes a clear drop. Removing graph traversal hurts more, because the model loses the ability to follow multi-hop dependencies. Removing audio access also causes a large decrease, especially for acoustic-aware questions.

Finally, we evaluate citation quality. On AMI, GRGA achieves much higher evidence precision than Qwen3-Omni and Text RAG. This confirms that GRGA is not only answering better, but also locating better supporting evidence.

## Slide 8: Conclusion

To conclude, this work makes three contributions.

First, we introduce **LongAudioQA**, a large-scale benchmark for long-form audio meeting QA, with more than 16 thousand question-answer pairs and five question types.

Second, we propose **GRGA**, a training-free graph-based retrieval-generation agent. It models meetings as multi-dimensional graphs and uses iterative planning to retrieve and verify evidence.

Third, our experiments show consistent improvements over Speech LLMs and RAG baselines, especially on inferential and acoustic-aware questions.

There are also limitations. GRGA still depends on upstream ASR and diarization quality, and iterative planning is slower than single-turn RAG.

In future work, we plan to extend this framework to streaming QA and broader long-form audio domains.

Thank you. I am happy to take questions.
