import ReactSlider from "react-slider";
import styles from "./Slider.module.css";
import {useRef,useState} from "react"

interface Props {
    max: number;
    currentIndex:number
    onChange:any
  }

function Slider(props:Props) {
    const { max, currentIndex,onChange } = props;
    const sliderRef = useRef<ReactSlider>(null);
    const [inputValue,setInputValue]=useState("")
    function onInputChange(e:any){
        setInputValue(e.target.value)
    }
    function onEnter(e:any){
        e.preventDefault()
        onChange(inputValue)
    }
    return (
        <div className={styles.mapper}>
            <div className={styles.sliderContainer}>
                <div key={1} className={styles.container}>
                    <span className={styles.label}>D{1}</span>
                    <ReactSlider
                    ref={sliderRef}
                    className={styles.slider}
                    markClassName={styles.mark}
                    onAfterChange={onChange}
                    defaultValue={0}
                    value={currentIndex}
                    orientation="vertical"
                    trackClassName={styles.track}
                    min={0}
                    max={max-1}
                    marks
                    invert
                    renderThumb={(thumbProps, state) => (
                        <div {...thumbProps} className={styles.thumb}>
                        {state.valueNow}
                        </div>
                    )}
                    />
                    <div className={styles.container}>
                        <form id="index_form">
                        <input type="number" value={inputValue} onChange={onInputChange} placeholder={currentIndex.toString()} id="keyInput"/>
                        </form>
                        <button type="submit" form="index_form" onClick={onEnter}>{"Enter"}</button>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default Slider;