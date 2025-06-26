// const EnhancedAccordion = ({ title, isOpen, onToggle, content, icon, canOpen, isLocked, onChangeClick, isCompleted }) => {
//     return (
//       <div
//         className={`bg-white rounded-lg border border-gray-300 overflow-hidden transition-all duration-300 ${
//           !canOpen ? "opacity-50 cursor-not-allowed" : ""
//         } ${isOpen ? "ring-2 ring-orange-200" : ""}`}
//       >
//         <div
//           className={`px-4 py-4 sm:px-6 flex justify-between items-center ${
//             isOpen ? "bg-gray-50 border-b border-gray-200" : "hover:bg-gray-50"
//           }`}
//           onClick={() => canOpen && !isLocked && onToggle()}
//           style={{ cursor: canOpen && !isLocked ? "pointer" : "default" }}
//         >
//           <div className="flex items-center space-x-3">
//             <div
//               className={`p-2 rounded-full ${isOpen ? "bg-orange-100 text-orange-700" : "bg-gray-100 text-gray-500"}`}
//             >
//               {/* Replace with your icon SVG or component */}
//               <span>{icon}</span>
//             </div>
//             <h3 className={`font-medium ${isOpen ? "text-orange-800" : "text-gray-700"}`}>{title}</h3>
//             {isCompleted && (
//               <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
//                 Completed
//               </span>
//             )}
//           </div>
//           {isLocked ? (
//             <button
//               onClick={(e) => {
//                 e.stopPropagation();
//                 onChangeClick();
//               }}
//               className="px-3 py-1 text-sm font-medium text-orange-600 hover:text-orange-700"
//             >
//               Change
//             </button>
//           ) : (
//             <div className={`transition-transform duration-300 ${isOpen ? "rotate-180" : ""}`}>
//               {/* Replace with your chevron SVG */}
//               <span>▼</span>
//             </div>
//           )}
//         </div>
//         {isOpen && (
//           <div className="max-h-96 overflow-y-auto">
//             <div className="p-4 sm:p-6 bg-white">{content}</div>
//           </div>
//         )}
//       </div>
//     );
//   };
  
//   export default EnhancedAccordion;