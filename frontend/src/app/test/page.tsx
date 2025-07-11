'use client';

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function Component() {

    const [url, setUrl] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [talkHistory, setTalkHistory] = useState(["aaaa","bbbb","cccc","dddd","eeee"]);
    const [conversationHistory, setConversationHistory] = useState([
        {
            id: 1,
            isUser: true,
            content: "aaaa",
        },
        {
            id: 2,
            isUser: false,
            content: "bbbb",
        },
        {
            id: 3,
            isUser: true,
            content: "cccc",
        },
        {
            id: 4,
            isUser: false,
            content: "dddd",
        }
    ]);
    const [adviceForExpression, setAdviceForExpression] = useState("aaa");
    const [alternativeExpressions, setAlternativeExpressions] = useState(['aaa','bbb','ccc']);
    const [usefulIdioms, setUsefulIdioms] = useState(['aaa','bbb','ccc']);
    const [isInvisible, setIsInvisible] = useState(false);
  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-100 via-blue-50 to-indigo-100 overflow-hidden">
      {/* 左サイドバー */}
      <div className="w-48 bg-gradient-to-b from-slate-800 to-slate-900 p-4 shadow-xl flex-shrink-0">
        <div className="mb-8">
          <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <div className="w-6 h-6 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full"></div>
            Talk History
          </h2>
          <div className="space-y-2">
            {talkHistory.map((_, i) => (
              <div
                key={i}
                className="text-slate-300 text-sm hover:text-white hover:bg-slate-700 p-2 rounded-lg cursor-pointer transition-all duration-200"
              >
                {_}
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-600 pt-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <div className="w-5 h-5 bg-gradient-to-r from-green-400 to-green-600 rounded-full"></div>
            Words Test
          </h3>
        </div>
      </div>

      {/* メインエリア */}
      <div className="flex-1 flex flex-col p-6 min-w-0">
        {/* ヘッダー部分 */}
        <div className="flex-shrink-0 mb-6">
          <h1 className="text-3xl font-bold text-slate-800 mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Talk Theme: Lorem ipsum dolor sit amet, consectetur
          </h1>

          <div className="flex gap-3">
            <div className="flex items-center gap-2 bg-white rounded-lg p-3 shadow-md border border-slate-200">
              <span className="text-slate-700 text-sm font-medium">URL:</span>
              <Input
                placeholder="URLを入力してください"
                className="w-64 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <Button className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all duration-200">
              Upload
            </Button>
          </div>
        </div>

        {/* 2つのウィンドウを並べる部分 - 残りの高さを全て使用 */}
        <div className="flex gap-6 flex-1 min-h-0">
          {/* Conversations History */}
          <div className="flex-1 bg-white rounded-xl shadow-lg border border-slate-200 flex flex-col min-w-0">
            <div className="flex items-center gap-3 p-6 pb-4 flex-shrink-0">
              <h2 className="text-2xl font-bold text-slate-800">Conversations History</h2>
              <Button
                variant="outline"
                size="sm"
                className="bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200 transition-colors duration-200"
              >
                Invisible
              </Button>
            </div>

            <div className="flex-1 px-6 pb-6 overflow-hidden">
              <div className="space-y-4 h-full overflow-y-auto">
                {conversationHistory.map((message) => (
                  <div key={message.id} className={`flex gap-3 ${message.isUser ? '' : 'flex-row-reverse'}`}>
                    <div className={`w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center shadow-md ${
                      message.isUser 
                        ? 'bg-gradient-to-r from-blue-500 to-blue-600' 
                        : 'bg-gradient-to-r from-green-500 to-green-600'
                    }`}>
                      <span className="text-white text-sm font-bold">
                        {message.isUser ? 'U' : 'AI'}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`text-sm font-semibold text-slate-700 mb-1 ${
                        message.isUser ? '' : 'text-right'
                      }`}>
                        {message.isUser ? 'User' : 'Models'}
                      </div>
                      <div className={`rounded-lg p-4 text-slate-700 text-sm shadow-sm ${
                        message.isUser 
                          ? 'bg-blue-50 border border-blue-100' 
                          : 'bg-green-50 border border-green-100'
                      }`}>
                        {message.content}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* English Skill-Up Report */}
          <div className="flex-1 bg-white rounded-xl shadow-lg border border-slate-200 flex flex-col min-w-0">
            <div className="flex items-center gap-3 p-6 pb-4 flex-shrink-0">
              <h2 className="text-2xl font-bold text-slate-800">English Skill-Up Report</h2>
            </div>

            <div className="flex-1 px-6 pb-6 overflow-hidden">
              <div className="space-y-4 h-full overflow-y-auto">
                {/* Advice for Expression */}
                <div>
                  <div className="text-sm font-semibold text-slate-700 mb-2">Advice for Expression</div>
                  <div className="bg-blue-50 rounded-lg p-4 text-slate-700 text-sm border border-blue-100 shadow-sm">
                    {adviceForExpression}
                  </div>
                </div>

                {/* Alternative Expressions */}
                <div>
                  <div className="text-sm font-semibold text-slate-700 mb-2">Alternative Expressions</div>
                  <div className="bg-green-50 rounded-lg p-4 text-slate-700 text-sm border border-green-100 shadow-sm">
                    <ul className="space-y-1">
                      {alternativeExpressions.map((expression) => (
                        <li key={expression}>{expression}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Useful Idioms */}
                <div>
                  <div className="text-sm font-semibold text-slate-700 mb-2">Useful Idioms</div>
                  <div className="bg-purple-50 rounded-lg p-4 text-slate-700 text-sm border border-purple-100 shadow-sm">
                    <ul className="space-y-1">
                      {usefulIdioms.map((idiom) => (
                        <li key={idiom}>{idiom}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
