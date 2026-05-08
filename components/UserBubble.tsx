interface UserBubbleProps {
  text: string;
}

export default function UserBubble({ text }: UserBubbleProps) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[72%] bg-logidex-navy text-white rounded-[18px] rounded-tr-[4px] px-[18px] py-[11px] text-[0.9rem] leading-relaxed">
        {text}
      </div>
    </div>
  );
}
